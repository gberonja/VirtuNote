from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List
from database.database import save_metadata, get_metadata, update_metadata, delete_metadata, list_all_metadata
from models.metadata import MetadataCreate, MetadataResponse
from utils.utils import verify_user

router = APIRouter()

@router.post("/", response_model=MetadataResponse)
def create_metadata(data: MetadataCreate, verified: str = Depends(verify_user)):
    saved = save_metadata(data.dict())
    return MetadataResponse(**saved)

@router.get("/", response_model=List[MetadataResponse])
def get_metadata_entry(
    score_id: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    verified: str = Depends(verify_user)
):
    try:
        metadata_list = list_all_metadata()

        if not metadata_list:
            raise HTTPException(status_code=404, detail="No metadata found")

        if query:
            metadata_list = [m for m in metadata_list if query.lower() in m["title"].lower()]

        return [MetadataResponse(**m) for m in metadata_list]

    except Exception as e:
        print(f"Error fetching metadata: {e}")
        raise HTTPException(status_code=500, detail="Metadata error: Internal Server Error")


@router.put("/", response_model=MetadataResponse)
def update_metadata_entry(
    score_id: str = Query(...),
    updates: dict = Body(...),
    verified: str = Depends(verify_user)
):
    updated = update_metadata(score_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return MetadataResponse(**updated)

@router.delete("/")
def delete_metadata_entry(
    score_id: str = Query(...),
    verified: str = Depends(verify_user)
):
    success = delete_metadata(score_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return {"detail": "Metadata deleted successfully"}
