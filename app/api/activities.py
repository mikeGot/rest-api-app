from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.repositories import ActivityRepository
from app.schemas import ActivityCreate, ActivityOut, ActivityTree, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=list[ActivityOut])
async def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    activity_repo = ActivityRepository(db)
    return await activity_repo.get_all(skip, limit)


@router.get("/tree", response_model=list[ActivityTree])
async def get_activities_tree(db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)):
    activity_repo = ActivityRepository(db)
    return await activity_repo.get_tree()


@router.get("/{activity_id}", response_model=ActivityOut)
async def get_activity(
    activity_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)
):
    activity_repo = ActivityRepository(db)
    activity = await activity_repo.get_by_id(activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found",
        )

    return activity


@router.post("/", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Create new activity (max 3 levels deep)"""
    activity_repo = ActivityRepository(db)
    try:
        return await activity_repo.create(activity_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/{activity_id}", response_model=ActivityOut)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Update activity"""
    activity_repo = ActivityRepository(db)
    try:
        activity = await activity_repo.update(activity_id, activity_data)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with id {activity_id} not found",
            )
        return activity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)
):
    """Delete activity"""
    activity_repo = ActivityRepository(db)
    deleted = await activity_repo.delete(activity_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found",
        )
