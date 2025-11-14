# from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.orm import relationship
#
# from database import Base
#
#
# class ValidationResult(Base):
#     __tablename__ = "validation_results"
#
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#
#
#     migration_job_id = Column(Integer, ForeignKey("migration_job.id"), nullable=False)
#
#
#     migration_job = relationship("MigrationJob", back_populates="validation_results")