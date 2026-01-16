import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Building
from app.repositories import BuildingRepository
from app.schemas import BuildingCreate, BuildingUpdate


@pytest.mark.unit
class TestBuildingRepository:
    async def test_create_building(self, test_session: AsyncSession):
        """Test creating a building."""
        repo = BuildingRepository(test_session)
        building_data = BuildingCreate(
            address="Test Street, 1", latitude=55.7558, longitude=37.6173
        )

        building = await repo.create(building_data)

        assert building.id is not None
        assert building.address == "Test Street, 1"
        assert building.latitude == 55.7558
        assert building.longitude == 37.6173

    async def test_get_building_by_id(self, test_session: AsyncSession, test_building: Building):
        """Test getting building by ID."""
        repo = BuildingRepository(test_session)

        building = await repo.get_by_id(test_building.id)

        assert building is not None
        assert building.id == test_building.id
        assert building.address == test_building.address

    async def test_get_building_by_id_not_found(self, test_session: AsyncSession):
        """Test getting non-existent building."""
        repo = BuildingRepository(test_session)

        building = await repo.get_by_id(9999)

        assert building is None

    async def test_get_all_buildings(self, test_session: AsyncSession, test_building: Building):
        """Test getting all buildings."""
        repo = BuildingRepository(test_session)

        buildings = await repo.get_all(skip=0, limit=10)

        assert len(buildings) >= 1
        assert any(b.id == test_building.id for b in buildings)

    async def test_update_building(self, test_session: AsyncSession, test_building: Building):
        """Test updating a building."""
        repo = BuildingRepository(test_session)
        update_data = BuildingUpdate(address="Updated Address")

        updated = await repo.update(test_building.id, update_data)

        assert updated is not None
        assert updated.address == "Updated Address"
        assert updated.latitude == test_building.latitude  # unchanged

    async def test_delete_building(self, test_session: AsyncSession, test_building: Building):
        """Test deleting a building."""
        repo = BuildingRepository(test_session)

        result = await repo.delete(test_building.id)
        assert result is True

        deleted = await repo.get_by_id(test_building.id)
        assert deleted is None

    async def test_delete_building_not_found(self, test_session: AsyncSession):
        """Test deleting non-existent building."""
        repo = BuildingRepository(test_session)

        result = await repo.delete(9999)

        assert result is False
