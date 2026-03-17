from fastapi import APIRouter

router = APIRouter(
    prefix="/migration-records",
    tags=["migration-records"]
)