from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models import Building, Organization, OrganizationPhone
from app.schemas import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        building_id: int | None = None,
        activity_id: int | None = None,
        activity_ids: list[int] | None = None,
    ) -> list[Organization]:
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )

        if building_id:
            query = query.where(Organization.building_id == building_id)

        if activity_id:
            query = query.join(Organization.activities).where(
                Organization.activities.any(id=activity_id)
            )

        if activity_ids:
            query = query.join(Organization.activities).where(
                or_(*[Organization.activities.any(id=aid) for aid in activity_ids])
            )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_id(self, organization_id: int) -> Organization | None:
        result = await self.db.execute(
            select(Organization)
            .where(Organization.id == organization_id)
            .options(
                joinedload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
        )
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def search_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> list[Organization]:
        result = await self.db.execute(
            select(Organization)
            .where(Organization.name.ilike(f"%{name}%"))
            .options(
                joinedload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def search_by_radius(
        self, latitude: float, longitude: float, radius_km: float, skip: int = 0, limit: int = 100
    ) -> list[Organization]:
        # Haversine formula for distance calculation
        # 6371 is Earth's radius in km

        # Calculate cosine of angle between points
        cos_angle = func.cos(func.radians(latitude)) * func.cos(
            func.radians(Building.latitude)
        ) * func.cos(func.radians(Building.longitude) - func.radians(longitude)) + func.sin(
            func.radians(latitude)
        ) * func.sin(
            func.radians(Building.latitude)
        )

        # Clamp value to [-1, 1] to avoid floating point errors in acos()
        cos_angle_clamped = func.least(1.0, func.greatest(-1.0, cos_angle))

        distance = func.acos(cos_angle_clamped) * 6371

        result = await self.db.execute(
            select(Organization)
            .join(Building)
            .where(distance <= radius_km)
            .options(
                joinedload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def search_by_rectangle(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Organization]:
        result = await self.db.execute(
            select(Organization)
            .join(Building)
            .where(
                and_(
                    Building.latitude >= min_lat,
                    Building.latitude <= max_lat,
                    Building.longitude >= min_lon,
                    Building.longitude <= max_lon,
                )
            )
            .options(
                joinedload(Organization.building),
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def create(self, organization_data: OrganizationCreate) -> Organization:
        org_dict = organization_data.model_dump(exclude={"phone_numbers", "activity_ids"})
        organization = Organization(**org_dict)

        # Add phones
        for phone_number in organization_data.phone_numbers:
            phone = OrganizationPhone(phone_number=phone_number)
            organization.phones.append(phone)

        # Add activities (will be loaded separately)
        self.db.add(organization)
        await self.db.flush()
        await self.db.refresh(organization)
        return organization

    async def update(
        self, organization_id: int, organization_data: OrganizationUpdate
    ) -> Organization | None:
        organization = await self.get_by_id(organization_id)
        if not organization:
            return None

        update_data = organization_data.model_dump(
            exclude_unset=True, exclude={"phone_numbers", "activity_ids"}
        )

        for field, value in update_data.items():
            setattr(organization, field, value)

        if organization_data.phone_numbers is not None:
            for phone in organization.phones:
                await self.db.delete(phone)
            organization.phones = []

            for phone_number in organization_data.phone_numbers:
                phone = OrganizationPhone(
                    phone_number=phone_number, organization_id=organization.id
                )
                organization.phones.append(phone)

        await self.db.flush()
        await self.db.refresh(organization, ["building", "phones", "activities"])
        return organization

    async def delete(self, organization_id: int) -> bool:
        organization = await self.get_by_id(organization_id)
        if not organization:
            return False

        await self.db.delete(organization)
        await self.db.flush()
        return True

    async def add_activities(
        self, organization_id: int, activity_ids: list[int]
    ) -> Organization | None:
        from app.models import Activity

        organization = await self.get_by_id(organization_id)
        if not organization:
            return None

        result = await self.db.execute(select(Activity).where(Activity.id.in_(activity_ids)))
        activities = list(result.scalars().all())

        existing_ids = {a.id for a in organization.activities}
        for activity in activities:
            if activity.id not in existing_ids:
                organization.activities.append(activity)

        await self.db.flush()
        await self.db.refresh(organization, ["activities"])
        return organization

    async def remove_activities(
        self, organization_id: int, activity_ids: list[int]
    ) -> Organization | None:
        organization = await self.get_by_id(organization_id)
        if not organization:
            return None

        organization.activities = [a for a in organization.activities if a.id not in activity_ids]

        await self.db.flush()
        await self.db.refresh(organization, ["activities"])
        return organization
