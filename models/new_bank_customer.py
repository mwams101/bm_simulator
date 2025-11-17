from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database import Base


class NewBankCustomer(Base):
    __tablename__ = "new_bank_customers"

    id = Column(Integer, primary_key=True, index=True)
    migration_job_id = Column(Integer, ForeignKey('job.id'), nullable=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    phone_masked = Column(String, nullable=False, index=True)
    address_line_1 = Column(String, nullable=False, index=True)
    address_line_2 = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    postal_code = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    customer_type = Column(postgresql.ENUM("individual", "business"), nullable=False, index=True)
    status = Column(postgresql.ENUM("active", "inactive", "suspend"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False, index=True)

    migration_job = relationship("MigrationJob", back_populates="new_bank_customers")