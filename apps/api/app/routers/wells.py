from fastapi import APIRouter

router = APIRouter()

@router.get("/wells/{well_id}")
async def well_detail(well_id: str):
    # Stub detail
    return {
        "id": well_id,
        "owner_name": "Doe Ranch, LLC",
        "county": "Travis",
        "date_completed": "2012-05-01",
        "borehole_depth_ft": 420,
        "proposed_use": "Domestic",
        "location_confidence": "medium",
        "documents": [
            {"type": "sdr_well_report", "url": "https://example.com/TWDB.pdf"}
        ]
    }