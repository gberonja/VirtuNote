from fastapi import APIRouter, File, UploadFile, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from datetime import datetime
import httpx
import logging
from io import BytesIO

from database.database import upload_to_s3, delete_from_s3, get_s3_key_from_url
from models.score import (
    ScoreResponse,
    ScoreUpdate,
    DeleteResponse
)
from utils.utils import verify_user, create_metadata, update_metadata, delete_metadata, fetch_metadata


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8000/users/login")
METADATA_API_URL = "http://metadataapi:8000/metadata/"


@router.post("/upload", response_model=ScoreResponse)
async def upload_score(
    title: str = Query(..., min_length=1, max_length=100),
    description: Optional[str] = Query(None, max_length=500),
    tags: str = Query("classical"),
    file: UploadFile = File(...),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="Only PDF files are allowed")

        file_content = await file.read()

        url = upload_to_s3(current_user, BytesIO(file_content), "pdf")
        score_id = url.split("/")[-1].split(".")[0]

        metadata = {
            "id": score_id,
            "user_id": current_user,
            "title": title,
            "description": description,
            "tags": tags,
            "file_url": url,
            "datum_unosa": datetime.utcnow().isoformat(),
            "komentari": [],
            "broj_likeova": 0
        }

        created_metadata = await create_metadata(metadata, token)
        return ScoreResponse(**created_metadata)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while creating metadata: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        logger.error(f"Error uploading score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ScoreResponse])
async def get_scores(
    title: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata_list = await fetch_metadata(user_id=current_user, token=token)

        if title:
            metadata_list = [
                m for m in metadata_list if title.lower() in m.get("title", "").lower()]

        if tags:
            metadata_list = [m for m in metadata_list if m.get("tags") in tags]

        return [ScoreResponse(**m) for m in metadata_list]

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while fetching metadata: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except Exception as e:
        logger.error(f"Error getting scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{score_id}", response_model=ScoreResponse)
async def get_score(
    score_id: str,
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata_list = await fetch_metadata(score_id=score_id, token=token)

        if not metadata_list:
            raise HTTPException(status_code=404, detail="Score not found")

        metadata = metadata_list[0]

        if metadata.get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Access denied")

        return ScoreResponse(**metadata)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while fetching score: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{score_id}", response_model=ScoreResponse)
async def update_score(
    score_id: str,
    score_update: ScoreUpdate,
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata_list = await fetch_metadata(score_id=score_id, token=token)

        if not metadata_list:
            raise HTTPException(status_code=404, detail="Score not found")

        metadata = metadata_list[0]

        if metadata.get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Access denied")

        updates = {k: v for k, v in score_update.dict().items()
                   if v is not None}
        updated_metadata = await update_metadata(score_id, updates, token)

        return ScoreResponse(**updated_metadata)

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while updating score: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error updating score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{score_id}", response_model=DeleteResponse)
async def delete_score(
    score_id: str,
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata_list = await fetch_metadata(score_id=score_id, token=token)

        if not metadata_list:
            raise HTTPException(status_code=404, detail="Score not found")

        metadata = metadata_list[0]

        if metadata.get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Access denied")

        file_url = metadata.get("file_url")
        if not file_url:
            raise HTTPException(status_code=404, detail="File not found")

        s3_key = get_s3_key_from_url(file_url)
        delete_from_s3(s3_key)

        await delete_metadata(score_id, token)

        return DeleteResponse()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while deleting score: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error deleting score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{score_id}/download")
async def download_score(
    score_id: str,
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata_list = await fetch_metadata(score_id=score_id, token=token)

        if not metadata_list:
            raise HTTPException(status_code=404, detail="Score not found")

        metadata = metadata_list[0]

        file_url = metadata.get("file_url")
        if not file_url:
            raise HTTPException(status_code=404, detail="File not found")

        return {"file_url": file_url}

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while getting download URL: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting download URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))
