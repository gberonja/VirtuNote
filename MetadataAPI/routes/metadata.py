from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List
import logging
from fastapi.security import OAuth2PasswordBearer

from database.database import (
    save_metadata,
    get_metadata,
    update_metadata,
    delete_metadata,
    list_all_metadata,
    add_comment,
    add_like
)
from models.metadata import (
    ScoreResponse,
    LikeResponse,
    DeleteResponse
)
from utils.utils import verify_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8000/users/login")


@router.post("/", response_model=ScoreResponse)
async def create_metadata_endpoint(
    data: dict = Body(...),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        if data.get("user_id") != current_user:
            raise HTTPException(
                status_code=403,
                detail="You can only create metadata for your own scores"
            )

        saved_metadata = save_metadata(data)
        return ScoreResponse(**saved_metadata)

    except Exception as e:
        logger.error(f"Error creating metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ScoreResponse])
async def get_metadata_endpoint(
    score_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        if score_id:
            metadata = get_metadata(score_id)
            if not metadata:
                raise HTTPException(
                    status_code=404, detail="Metadata not found")
            return [ScoreResponse(**metadata)]

        items = list_all_metadata(
            user_id=user_id, tags=tags, title_contains=title)
        return [ScoreResponse(**item) for item in items]

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error fetching metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", response_model=ScoreResponse)
async def update_metadata_endpoint(
    score_id: str = Query(...),
    updates: dict = Body(...),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata = get_metadata(score_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        if metadata.get("user_id") != current_user:
            raise HTTPException(
                status_code=403,
                detail="You can only update metadata for your own scores"
            )

        updated_metadata = update_metadata(score_id, updates)
        if not updated_metadata:
            raise HTTPException(
                status_code=500,
                detail="Failed to update metadata"
            )

        return ScoreResponse(**updated_metadata)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/", response_model=DeleteResponse)
async def delete_metadata_endpoint(
    score_id: str = Query(...),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata = get_metadata(score_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")

        if metadata.get("user_id") != current_user:
            raise HTTPException(
                status_code=403,
                detail="You can only delete metadata for your own scores"
            )

        success = delete_metadata(score_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete metadata"
            )

        return DeleteResponse(message="Metadata deleted successfully")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error deleting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{score_id}/like", response_model=LikeResponse)
async def like_score_endpoint(
    score_id: str,
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata = get_metadata(score_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Score not found")

        likes_by_users = metadata.get("likes_by_users", [])
        if current_user in likes_by_users:
            return LikeResponse(
                score_id=score_id,
                broj_likeova=metadata.get("broj_likeova", 0),
                message="You have already liked this score"
            )

        updated_metadata = add_like(score_id, current_user)
        if not updated_metadata:
            raise HTTPException(
                status_code=500,
                detail="Failed to add like"
            )

        return LikeResponse(
            score_id=score_id,
            broj_likeova=updated_metadata.get("broj_likeova", 0)
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error adding like: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{score_id}/comment", response_model=ScoreResponse)
async def comment_score_endpoint(
    score_id: str,
    comment: str = Body(..., embed=True),
    current_user: str = Depends(verify_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        metadata = get_metadata(score_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Score not found")

        updated_metadata = add_comment(score_id, current_user, comment)
        if not updated_metadata:
            raise HTTPException(
                status_code=500,
                detail="Failed to add comment"
            )

        return ScoreResponse(**updated_metadata)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
