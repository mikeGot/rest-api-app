import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Activity
from app.repositories import ActivityRepository
from app.schemas import ActivityCreate


@pytest.mark.unit
class TestActivityRepository:
    async def test_create_root_activity(self, test_session: AsyncSession):
        """Test creating root activity."""
        repo = ActivityRepository(test_session)
        activity_data = ActivityCreate(name="Root Activity", parent_id=None)

        activity = await repo.create(activity_data)

        assert activity.id is not None
        assert activity.name == "Root Activity"
        assert activity.level == 1
        assert activity.parent_id is None

    async def test_create_child_activity(self, test_session: AsyncSession, test_activity: Activity):
        """Test creating child activity."""
        repo = ActivityRepository(test_session)
        child_data = ActivityCreate(name="Child Activity", parent_id=test_activity.id)

        child = await repo.create(child_data)

        assert child.id is not None
        assert child.name == "Child Activity"
        assert child.level == 2
        assert child.parent_id == test_activity.id

    async def test_create_activity_level_3(self, test_session: AsyncSession):
        """Test creating activity at level 3."""
        repo = ActivityRepository(test_session)

        # Create level 1
        level1 = await repo.create(ActivityCreate(name="Level 1", parent_id=None))

        # Create level 2
        level2 = await repo.create(ActivityCreate(name="Level 2", parent_id=level1.id))

        # Create level 3
        level3 = await repo.create(ActivityCreate(name="Level 3", parent_id=level2.id))

        assert level3.level == 3

    async def test_create_activity_level_4_fails(self, test_session: AsyncSession):
        """Test that creating level 4 activity raises error."""
        repo = ActivityRepository(test_session)

        # Create levels 1-3
        level1 = await repo.create(ActivityCreate(name="Level 1", parent_id=None))
        level2 = await repo.create(ActivityCreate(name="Level 2", parent_id=level1.id))
        level3 = await repo.create(ActivityCreate(name="Level 3", parent_id=level2.id))

        # Try to create level 4
        with pytest.raises(ValueError, match="nesting level cannot exceed 3"):
            await repo.create(ActivityCreate(name="Level 4", parent_id=level3.id))

    async def test_get_all_descendants(
        self, test_session: AsyncSession, test_activities_tree: list[Activity]
    ):
        """Test getting all descendant IDs."""
        repo = ActivityRepository(test_session)
        root = test_activities_tree[0]

        descendants = await repo.get_all_descendants(root.id)

        assert len(descendants) == 4
        assert root.id in descendants

    async def test_get_tree(self, test_session: AsyncSession, test_activities_tree: list[Activity]):
        """Test getting activity tree."""
        repo = ActivityRepository(test_session)

        tree = await repo.get_tree()

        assert len(tree) == 1
        root = tree[0]
        assert len(root.children) == 2
