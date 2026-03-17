from pydantic import BaseModel


class MigrationRecordsBase(BaseModel):
    id: int
