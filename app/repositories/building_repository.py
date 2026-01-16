from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Building
from app.schemas import BuildingCreate, BuildingUpdate


class BuildingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Building]:
        result = await self.db.execute(select(Building).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, building_id: int) -> Building | None:
        result = await self.db.execute(select(Building).where(Building.id == building_id))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def create(self, building_data: BuildingCreate) -> Building:
        building = Building(**building_data.model_dump())
        self.db.add(building)
        await self.db.flush()
        await self.db.refresh(building)
        return building

    async def update(self, building_id: int, building_data: BuildingUpdate) -> Building | None:
        building = await self.get_by_id(building_id)
        if not building:
            return None

        update_data = building_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(building, field, value)

        await self.db.flush()
        await self.db.refresh(building)
        return building

    async def delete(self, building_id: int) -> bool:
        building = await self.get_by_id(building_id)
        if not building:
            return False

        await self.db.delete(building)
        await self.db.flush()
        return True
