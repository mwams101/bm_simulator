import enum

from sqlalchemy import Column, Integer, ForeignKey, Float, String, Date, DateTime, Enum
from sqlalchemy.orm import relationship

from database import Base


class NewBankAccountAccountType(enum.Enum):
    SAVINGS = 'savings'
    CHECKING = 'checking'
    CREDIT = 'credit'
    LOAN = 'loan'


class NewBankAccountAccountStatus(enum.Enum):
    ACTIVE = 'active'
    CLOSED = 'closed'
    FROZEN = 'frozen'


class NewBankAccount(Base):
    __tablename__ = "new_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("new_bank_customers.id"), index=True, nullable=False)
    migration_job_id = Column(Integer, ForeignKey("migration_jobs.id"), index=True, nullable=True)

    account_number = Column(Integer, unique=True, index=True, nullable=False)
    account_type = Column(Enum(NewBankAccountAccountType), index=True, nullable=False)
    balance = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    account_open_date = Column(Date, nullable=False)
    status = Column(Enum(NewBankAccountAccountStatus), nullable=False)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    customer = relationship("NewBankCustomer", back_populates="new_bank_accounts")
    migration_job = relationship("MigrationJob", back_populates="new_bank_accounts")
