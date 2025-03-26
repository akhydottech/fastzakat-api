from fastapi import APIRouter

from app.models import AddressResponse
from app.utils import address_search

router = APIRouter(prefix="/address", tags=["address"])

@router.get("/search", response_model=AddressResponse)
def search_address(query: str):
    return address_search(query)
