from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

import models
from db.session import get_db
from modules.security.auth import require_admin
from schemas.new_bank_customers import NewBankCustomersBase, NewBankCustomersCreate, NewBankCustomersUpdate

router = APIRouter(
    prefix="/new-bank-customers",
    tags=["new-bank-customers"]
)


@router.get("/", response_model=List[NewBankCustomersBase])
async def get_new_bank_customers(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    return db.query(models.NewBankCustomer).all()


@router.get("/{customer_id}", response_model=NewBankCustomersBase)
async def get_new_bank_customer_by_id(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    customer = db.query(models.NewBankCustomer).filter(
        models.NewBankCustomer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.post("/", response_model=NewBankCustomersBase)
async def create_new_bank_customer(
        customer: NewBankCustomersCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.NewBankCustomer).filter(
        models.NewBankCustomer.email == customer.email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")

    new_customer = models.NewBankCustomer(
        migration_job_id=customer.migration_job_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        date_of_birth=customer.date_of_birth,
        email=customer.email,
        phone_masked=customer.phone_masked,
        address_line_1=customer.address_line_1,
        address_line_2=customer.address_line_2,
        city=customer.city,
        state=customer.state,
        postal_code=customer.postal_code,
        country=customer.country,
        customer_type=customer.customer_type,
        status=customer.status,
        created_at=customer.created_at,
        updated_at=customer.updated_at
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@router.put("/{customer_id}", response_model=NewBankCustomersBase)
async def update_new_bank_customer(
        customer_id: int,
        customer: NewBankCustomersUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    existing = db.query(models.NewBankCustomer).filter(
        models.NewBankCustomer.id == customer_id
    ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")

    existing.first_name = customer.first_name
    existing.last_name = customer.last_name
    existing.email = customer.email
    existing.phone_masked = customer.phone_masked
    existing.address_line_1 = customer.address_line_1
    existing.address_line_2 = customer.address_line_2
    existing.city = customer.city
    existing.state = customer.state
    existing.postal_code = customer.postal_code
    existing.country = customer.country
    existing.status = customer.status
    existing.updated_at = customer.updated_at

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{customer_id}")
async def delete_new_bank_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(require_admin)
):
    customer = db.query(models.NewBankCustomer).filter(
        models.NewBankCustomer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer successfully deleted"}