from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.new_bank_accounts import NewBankAccountsBase, NewBankAccountsCreate, NewBankAccountsUpdate

router = APIRouter(
    prefix="/new-bank-accounts",
    tags=["new-bank-accounts"]
)


@router.get("/", response_model=List[NewBankAccountsBase])
async def get_new_bank_accounts(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.NewBankAccount).all()


@router.get("/{account_id}", response_model=NewBankAccountsBase)
async def get_new_bank_account_by_id(
        account_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    account = db.query(models.NewBankAccount).filter(
        models.NewBankAccount.id == account_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.get("/by-customer/{customer_id}", response_model=List[NewBankAccountsBase])
async def get_new_bank_accounts_by_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.NewBankAccount).filter(
        models.NewBankAccount.customer_id == customer_id
    ).all()


@router.post("/", response_model=NewBankAccountsBase)
async def create_new_bank_account(
        account: NewBankAccountsCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.NewBankAccount).filter(
        models.NewBankAccount.account_number == account.account_number
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Account with this account number already exists")

    customer = db.query(models.NewBankCustomer).filter(
        models.NewBankCustomer.id == account.customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    new_account = models.NewBankAccount(
        customer_id=account.customer_id,
        migration_job_id=account.migration_job_id,
        account_number=account.account_number,
        account_type=account.account_type,
        balance=account.balance,
        currency=account.currency,
        account_open_date=account.account_open_date,
        status=account.status,
        created_at=account.created_at,
        updated_at=account.updated_at
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account


@router.put("/{account_id}", response_model=NewBankAccountsBase)
async def update_new_bank_account(
        account_id: int,
        account: NewBankAccountsUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.NewBankAccount).filter(
        models.NewBankAccount.id == account_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Account not found")

    existing.balance = account.balance
    existing.status = account.status
    existing.updated_at = account.updated_at

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{account_id}")
async def delete_new_bank_account(
        account_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    account = db.query(models.NewBankAccount).filter(
        models.NewBankAccount.id == account_id
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account)
    db.commit()

    return {"message": "Account successfully deleted"}