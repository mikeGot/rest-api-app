from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization
from app.repositories import ActivityRepository, OrganizationRepository
from app.schemas import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.activity_repo = ActivityRepository(db)

    async def search_by_activity(
        self, activity_id: int, include_descendants: bool = True, skip: int = 0, limit: int = 100
    ) -> list[Organization]:
        """Search organizations by activity, optionally including child activities"""
        if include_descendants:
            activity_ids = await self.activity_repo.get_all_descendants(activity_id)
            return await self.org_repo.get_all(skip=skip, limit=limit, activity_ids=activity_ids)
        else:
            return await self.org_repo.get_all(skip=skip, limit=limit, activity_id=activity_id)

    async def create_with_activities(self, organization_data: OrganizationCreate) -> Organization:
        """Create organization and associate with activities"""
        organization = await self.org_repo.create(organization_data)

        if organization_data.activity_ids:
            await self.org_repo.add_activities(organization.id, organization_data.activity_ids)
            await self.db.refresh(organization, ["activities"])

        return organization

    async def update_with_activities(
        self, organization_id: int, organization_data: OrganizationUpdate
    ) -> Organization | None:
        """Update organization and its activities"""
        organization = await self.org_repo.update(organization_id, organization_data)
        if not organization:
            return None

        if organization_data.activity_ids is not None:
            existing_ids = [a.id for a in organization.activities]
            if existing_ids:
                await self.org_repo.remove_activities(organization_id, existing_ids)

            if organization_data.activity_ids:
                await self.org_repo.add_activities(organization_id, organization_data.activity_ids)

            await self.db.refresh(organization, ["activities"])

        return organization
