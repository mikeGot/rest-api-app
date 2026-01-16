import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Building, Organization
from app.repositories import OrganizationRepository
from app.schemas import OrganizationCreate


@pytest.mark.unit
class TestOrganizationRepository:
    async def test_create_organization(self, test_session: AsyncSession, test_building: Building):
        """Test creating organization."""
        repo = OrganizationRepository(test_session)
        org_data = OrganizationCreate(
            name="Test Org",
            building_id=test_building.id,
            phone_numbers=["123-456-789"],
            activity_ids=[],
        )

        org = await repo.create(org_data)

        await test_session.refresh(org, ["phones"])

        assert org.id is not None
        assert org.name == "Test Org"
        assert org.building_id == test_building.id
        assert len(org.phones) == 1
        assert org.phones[0].phone_number == "123-456-789"

    async def test_get_organization_by_id(
        self, test_session: AsyncSession, test_organization: Organization
    ):
        """Test getting organization by ID."""
        repo = OrganizationRepository(test_session)

        org = await repo.get_by_id(test_organization.id)

        assert org is not None
        assert org.id == test_organization.id
        assert org.building is not None
        assert len(org.phones) > 0
        assert len(org.activities) > 0

    async def test_search_by_name(
        self, test_session: AsyncSession, test_organization: Organization
    ):
        """Test searching organization by name."""
        repo = OrganizationRepository(test_session)

        results = await repo.search_by_name("Test")

        assert len(results) >= 1
        assert any(o.id == test_organization.id for o in results)

    async def test_get_all_by_building(
        self, test_session: AsyncSession, test_organization: Organization
    ):
        """Test getting organizations by building."""
        repo = OrganizationRepository(test_session)

        results = await repo.get_all(building_id=test_organization.building_id)

        assert len(results) >= 1
        assert any(o.id == test_organization.id for o in results)

    async def test_add_activities(
        self, test_session: AsyncSession, test_organization: Organization
    ):
        """Test adding activities to organization."""
        repo = OrganizationRepository(test_session)
        initial_count = len(test_organization.activities)

        from app.models import Activity

        new_activity = Activity(name="New Activity", level=1)
        test_session.add(new_activity)
        await test_session.commit()
        await test_session.refresh(new_activity)

        updated = await repo.add_activities(test_organization.id, [new_activity.id])

        assert updated is not None
        assert len(updated.activities) == initial_count + 1

    async def test_delete_organization(
        self, test_session: AsyncSession, test_organization: Organization
    ):
        """Test deleting organization."""
        repo = OrganizationRepository(test_session)

        result = await repo.delete(test_organization.id)
        assert result is True

        deleted = await repo.get_by_id(test_organization.id)
        assert deleted is None
