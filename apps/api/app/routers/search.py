from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter()

@router.get("/search")
async def search(q: Optional[str] = Query(default="")):
    """Stubbed search endpoint. Replace with PostGIS-powered query.
    Returns a couple of fake wells near Austin to prove the flow.
    """
    items = [
        {"id": "SDR-123", "owner_name": "Doe Ranch, LLC", "county": "Travis", "lat": 30.2672, "lon": -97.7431},
        {"id": "SDR-456", "owner_name": "Smith Farms", "county": "Hays", "lat": 30.0394, "lon": -97.8806}
    ]
    return {"items": items}