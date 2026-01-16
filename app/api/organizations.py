from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.repositories import OrganizationRepository
from app.schemas import OrganizationCreate, OrganizationOut, OrganizationUpdate
from app.services import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[OrganizationOut])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    building_id: int | None = Query(None, description="Filter by building ID"),
    activity_id: int
    | None = Query(None, description="Filter by activity ID (includes descendants)"),
    latitude: float | None = Query(None, ge=-90, le=90, description="Latitude for geo search"),
    longitude: float | None = Query(None, ge=-180, le=180, description="Longitude for geo search"),
    radius_km: float | None = Query(None, gt=0, description="Radius in km for geo search"),
    min_lat: float
    | None = Query(None, ge=-90, le=90, description="Min latitude for rectangle search"),
    min_lon: float
    | None = Query(None, ge=-180, le=180, description="Min longitude for rectangle search"),
    max_lat: float
    | None = Query(None, ge=-90, le=90, description="Max latitude for rectangle search"),
    max_lon: float
    | None = Query(None, ge=-180, le=180, description="Max longitude for rectangle search"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """
    Get list of organizations with optional filtering:
    - Filter by building_id
    - Filter by activity_id (includes all descendants in the activity tree)
    - Geo search by radius: specify latitude, longitude, and radius_km
    - Geo search by bounding box: specify min_lat, min_lon, max_lat, max_lon
    """
    org_repo = OrganizationRepository(db)
    org_service = OrganizationService(db)

    if latitude is not None and longitude is not None and radius_km is not None:
        return await org_repo.search_by_radius(latitude, longitude, radius_km, skip, limit)

    if min_lat is not None and min_lon is not None and max_lat is not None and max_lon is not None:
        return await org_repo.search_by_rectangle(min_lat, min_lon, max_lat, max_lon, skip, limit)

    if activity_id is not None:
        return await org_service.search_by_activity(
            activity_id, include_descendants=True, skip=skip, limit=limit
        )

    return await org_repo.get_all(skip, limit, building_id=building_id)


@router.get("/search", response_model=list[OrganizationOut])
async def search_organizations(
    name: str | None = Query(None, description="Search by organization name"),
    activity_id: int
    | None = Query(None, description="Filter by activity ID (includes descendants)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """
    Search organizations by name or activity.
    Activity search includes all descendants in the activity tree.
    """
    org_repo = OrganizationRepository(db)
    org_service = OrganizationService(db)

    if name:
        return await org_repo.search_by_name(name, skip, limit)

    if activity_id is not None:
        return await org_service.search_by_activity(
            activity_id, include_descendants=True, skip=skip, limit=limit
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provide at least one search parameter: name or activity_id",
    )


@router.get("/{organization_id}", response_model=OrganizationOut)
async def get_organization(
    organization_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)
):
    """Get organization by ID with full details"""
    org_repo = OrganizationRepository(db)
    organization = await org_repo.get_by_id(organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id {organization_id} not found",
        )

    return organization


@router.post("/", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Create new organization with phones and activities"""
    org_service = OrganizationService(db)
    return await org_service.create_with_activities(organization_data)


@router.put("/{organization_id}", response_model=OrganizationOut)
async def update_organization(
    organization_id: int,
    organization_data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Update organization"""
    org_service = OrganizationService(db)
    organization = await org_service.update_with_activities(organization_id, organization_data)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id {organization_id} not found",
        )

    return organization


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: int, db: AsyncSession = Depends(get_db), _: str = Depends(verify_api_key)
):
    """Delete organization"""
    org_repo = OrganizationRepository(db)
    deleted = await org_repo.delete(organization_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with id {organization_id} not found",
        )
