"""
Execution Service — Stage 3 of the migration pipeline.

Responsibility:
    - Commit all validation-SUCCESS MigrationRecords to the destination tables
      (NewBankCustomer and NewBankAccount)
    - Each record is wrapped in a savepoint so a single failure does not
      roll back the entire batch
    - Update MigrationRecord.migrated_at on success, or mark FAILED with an
      error message on per-record failure
    - Advance the job status from PREVIEWING → EXECUTING → COMPLETED
      (or FAILED if every record fails)

Field routing (customer vs account):
    The execution service needs to know which destination fields belong to
    NewBankCustomer and which belong to NewBankAccount.

    This is controlled via FieldMapping.mapping_rules JSON:
        {
          "customer_fields": ["first_name", "last_name", "email", ...],
          "account_fields":  ["account_number", "account_type", "balance", ...]
        }

    If those keys are absent, the service falls back to DEFAULT_CUSTOMER_FIELDS
    and DEFAULT_ACCOUNT_FIELDS defined below.

Idempotency:
    Before creating a customer, the service checks for an existing NewBankCustomer
    with the same email under this job. Likewise for account_number on NewBankAccount.
    Duplicate records are skipped (counted as successful) rather than erroring.
"""

from datetime import datetime, date
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
from models.migration_job import JobStatus
from models.migration_record import MigrationRecordStatus
from models.new_bank_customer import NewBankCustomer, NewBankCustomerStatus, NewBankCustomerType
from models.new_bank_account import NewBankAccount, NewBankAccountAccountStatus, NewBankAccountAccountType


# ---------------------------------------------------------------------------
# Default field sets — used when mapping_rules does not specify them
# ---------------------------------------------------------------------------

DEFAULT_CUSTOMER_FIELDS = {
    "first_name", "last_name", "date_of_birth", "email", "phone_masked",
    "address_line_1", "address_line_2", "city", "state", "postal_code",
    "country", "customer_type", "customer_status",
}

DEFAULT_ACCOUNT_FIELDS = {
    "account_number", "account_type", "balance", "currency",
    "account_open_date", "account_status",
}


# ---------------------------------------------------------------------------
# Type coercion helpers
# ---------------------------------------------------------------------------

def _to_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except (ValueError, TypeError):
            continue
    raise ValueError(f"Cannot parse '{value}' as a date. Expected formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY")


def _to_float(value) -> float:
    try:
        return float(str(value).replace(",", ""))
    except (ValueError, TypeError):
        raise ValueError(f"Cannot parse '{value}' as a number")


def _to_int(value) -> int:
    try:
        return int(str(value).replace(",", "").split(".")[0])
    except (ValueError, TypeError):
        raise ValueError(f"Cannot parse '{value}' as an integer")


def _to_enum(enum_class, value, field_name: str):
    if value is None:
        return None
    str_val = str(value).lower()
    for member in enum_class:
        if member.value == str_val:
            return member
    valid = [m.value for m in enum_class]
    raise ValueError(f"Invalid value '{value}' for {field_name}. Expected one of: {valid}")


# ---------------------------------------------------------------------------
# Customer and account builders
# ---------------------------------------------------------------------------

def _build_customer(data: dict, job_id: int, now: datetime) -> NewBankCustomer:
    return NewBankCustomer(
        migration_job_id=job_id,
        first_name=data.get("first_name") or "",
        last_name=data.get("last_name") or "",
        date_of_birth=_to_date(data.get("date_of_birth")),
        email=data.get("email") or "",
        phone_masked=data.get("phone_masked") or "",
        address_line_1=data.get("address_line_1") or "",
        address_line_2=data.get("address_line_2") or "",
        city=data.get("city") or "",
        state=data.get("state") or "",
        postal_code=data.get("postal_code") or "",
        country=data.get("country") or "",
        customer_type=_to_enum(
            NewBankCustomerType,
            data.get("customer_type", "individual"),
            "customer_type"
        ),
        status=_to_enum(
            NewBankCustomerStatus,
            data.get("customer_status", "active"),
            "customer_status"
        ),
        created_at=now,
        updated_at=now,
    )


def _build_account(data: dict, customer_id: int, job_id: int, now: datetime) -> NewBankAccount:
    return NewBankAccount(
        customer_id=customer_id,
        migration_job_id=job_id,
        account_number=_to_int(data.get("account_number")),
        account_type=_to_enum(
            NewBankAccountAccountType,
            data.get("account_type", "savings"),
            "account_type"
        ),
        balance=_to_float(data.get("balance", 0)),
        currency=data.get("currency") or "USD",
        account_open_date=_to_date(data.get("account_open_date")),
        status=_to_enum(
            NewBankAccountAccountStatus,
            data.get("account_status", "active"),
            "account_status"
        ),
        created_at=now,
        updated_at=now,
    )


# ---------------------------------------------------------------------------
# Main service entry point
# ---------------------------------------------------------------------------

def run(job_id: int, db: Session) -> dict:
    """
    Execute the migration for all validated records in a job.

    Args:
        job_id: ID of the MigrationJob to process.
        db:     Active SQLAlchemy session.

    Returns:
        dict with committed, skipped, failed counts and final job status.
    """

    # 1. Load and validate job state
    job = db.query(models.MigrationJob).filter(models.MigrationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Migration job not found")
    if job.status != JobStatus.PREVIEWING:
        raise HTTPException(
            status_code=400,
            detail=f"Job must be in PREVIEWING status to execute. Current status: {job.status.value}"
        )

    # 2. Advance to EXECUTING
    job.status = JobStatus.EXECUTING
    db.commit()

    try:
        # 3. Load all SUCCESS records from the validation stage
        records: List[models.MigrationRecord] = (
            db.query(models.MigrationRecord)
            .filter(
                models.MigrationRecord.migration_job_id == job_id,
                models.MigrationRecord.status == MigrationRecordStatus.SUCCESS
            )
            .all()
        )
        if not records:
            raise HTTPException(
                status_code=400,
                detail="No validated records found to execute. Run validation first."
            )

        # 4. Resolve field routing from mapping_rules (or fall back to defaults)
        field_mapping = (
            db.query(models.FieldMapping)
            .filter(models.FieldMapping.migration_job_id == job_id)
            .first()
        )
        mapping_config = field_mapping.mapping_rules if field_mapping else {}
        customer_fields = set(mapping_config.get("customer_fields", DEFAULT_CUSTOMER_FIELDS))
        account_fields = set(mapping_config.get("account_fields", DEFAULT_ACCOUNT_FIELDS))

        now = datetime.utcnow()
        committed = 0
        skipped = 0
        failed = 0

        # 5. Process each record inside a savepoint for per-record isolation
        for record in records:
            data: dict = record.transformed_data or {}

            customer_data = {k: v for k, v in data.items() if k in customer_fields}
            account_data = {k: v for k, v in data.items() if k in account_fields}

            try:
                with db.begin_nested():  # savepoint — failure rolls back only this record
                    # -- Idempotency check for customer --
                    email = customer_data.get("email")
                    existing_customer = None
                    if email:
                        existing_customer = (
                            db.query(NewBankCustomer)
                            .filter(
                                NewBankCustomer.migration_job_id == job_id,
                                NewBankCustomer.email == email
                            )
                            .first()
                        )

                    if existing_customer:
                        customer = existing_customer
                        skipped += 1
                    else:
                        customer = _build_customer(customer_data, job_id, now)
                        db.add(customer)
                        db.flush()  # get customer.id before creating account

                    # -- Idempotency check for account --
                    account_number = account_data.get("account_number")
                    existing_account = None
                    if account_number:
                        existing_account = (
                            db.query(NewBankAccount)
                            .filter(NewBankAccount.account_number == _to_int(account_number))
                            .first()
                        )

                    if not existing_account:
                        account = _build_account(account_data, customer.id, job_id, now)
                        db.add(account)

                record.migrated_at = now
                if skipped == 0 or not existing_customer:
                    committed += 1

            except Exception as e:
                record.status = MigrationRecordStatus.FAILED
                record.error_message = str(e)
                failed += 1

        # 6. Update job counters and status
        job.successful_records = committed + skipped
        job.failed_records = failed
        job.completed_at = now
        job.status = JobStatus.FAILED if committed == 0 and skipped == 0 else JobStatus.COMPLETED
        db.commit()

        return {
            "committed": committed,
            "skipped_duplicates": skipped,
            "failed": failed,
            "status": job.status.value,
        }

    except HTTPException:
        job.status = JobStatus.FAILED
        job.error_message = "Execution stage failed — see logs"
        db.commit()
        raise
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")