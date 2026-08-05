from fastapi import APIRouter

from ..services import db_service

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/filters")
def get_filters():
    return db_service.load_filter_options()
