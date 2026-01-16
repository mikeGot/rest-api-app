from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.repositories import BuildingRepository
from app.schemas import BuildingCreate, BuildingOut, BuildingUpdate

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/", response_model=list[BuildingOut])
async def get_buildings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Get list of all buildings"""
    building_repo = BuildingRepository(db)
    return await building_repo.get_all(skip, limit)


@router.get("/{building_id}", response_model=BuildingOut)
async def get_building(
    building_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)
):
    """Get building by ID"""
    building_repo = BuildingRepository(db)
    building = await building_repo.get_by_id(building_id)

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building with id {building_id} not found",
        )

    return building


@router.post("/", response_model=BuildingOut, status_code=status.HTTP_201_CREATED)
async def create_building(
    building_data: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Create new building"""
    building_repo = BuildingRepository(db)
    return await building_repo.create(building_data)


@router.put("/{building_id}", response_model=BuildingOut)
async def update_building(
    building_id: int,
    building_data: BuildingUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Update building"""
    building_repo = BuildingRepository(db)
    building = await building_repo.update(building_id, building_data)

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building with id {building_id} not found",
        )

    return building


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    building_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)
):
    """Delete building"""
    building_repo = BuildingRepository(db)
    deleted = await building_repo.delete(building_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Building with id {building_id} not found",
        )
