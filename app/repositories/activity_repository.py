from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Activity
from app.schemas import ActivityCreate, ActivityUpdate


class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Activity]:
        result = await self.db.execute(select(Activity).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, activity_id: int) -> Activity | None:
        result = await self.db.execute(select(Activity).where(Activity.id == activity_id))
        return result.scalar_one_or_none()  # type: ignore[no-any-return]

    async def get_tree(self) -> list[Activity]:
        """Get all root activities with children loaded (3 levels deep)"""
        result = await self.db.execute(
            select(Activity)
            .where(Activity.parent_id.is_(None))
            .options(
                selectinload(Activity.children)
                .selectinload(Activity.children)
                .selectinload(Activity.children)
            )
        )
        return list(result.scalars().all())

    async def get_all_descendants(self, activity_id: int) -> list[int]:
        """Get all descendant activity IDs including the given one using recursive CTE"""
        from sqlalchemy import text

        query = text(
            """
            WITH RECURSIVE descendants AS (
                SELECT id FROM activities WHERE id = :activity_id
                UNION ALL
                SELECT a.id
                FROM activities a
                INNER JOIN descendants d ON a.parent_id = d.id
            )
            SELECT id FROM descendants
        """
        )

        result = await self.db.execute(query, {"activity_id": activity_id})
        return [row[0] for row in result.fetchall()]

    async def create(self, activity_data: ActivityCreate) -> Activity:
        level = 1
        if activity_data.parent_id:
            parent = await self.get_by_id(activity_data.parent_id)
            if parent:
                level = parent.level + 1
                if level > 3:
                    raise ValueError("Activity nesting level cannot exceed 3")

        activity = Activity(**activity_data.model_dump(), level=level)
        self.db.add(activity)
        await self.db.flush()
        await self.db.refresh(activity)
        return activity

    async def update(self, activity_id: int, activity_data: ActivityUpdate) -> Activity | None:
        activity = await self.get_by_id(activity_id)
        if not activity:
            return None

        update_data = activity_data.model_dump(exclude_unset=True)

        if "parent_id" in update_data:
            if update_data["parent_id"]:
                parent = await self.get_by_id(update_data["parent_id"])
                if parent:
                    new_level = parent.level + 1
                    if new_level > 3:
                        raise ValueError("Activity nesting level cannot exceed 3")
                    update_data["level"] = new_level
            else:
                update_data["level"] = 1

        for field, value in update_data.items():
            setattr(activity, field, value)

        await self.db.flush()
        await self.db.refresh(activity)
        return activity

    async def delete(self, activity_id: int) -> bool:
        activity = await self.get_by_id(activity_id)
        if not activity:
            return False

        await self.db.delete(activity)
        await self.db.flush()
        return True
