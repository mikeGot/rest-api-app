import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app
from app.models import Activity, Building, Organization, OrganizationPhone

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
async def test_building(test_session: AsyncSession) -> Building:
    """Create test building."""
    building = Building(address="Test Address, 123", latitude=55.7558, longitude=37.6173)
    test_session.add(building)
    await test_session.commit()
    await test_session.refresh(building)
    return building


@pytest.fixture
async def test_activity(test_session: AsyncSession) -> Activity:
    """Create test activity."""
    activity = Activity(name="Test Activity", level=1, parent_id=None)
    test_session.add(activity)
    await test_session.commit()
    await test_session.refresh(activity)
    return activity


@pytest.fixture
async def test_organization(
    test_session: AsyncSession, test_building: Building, test_activity: Activity
) -> Organization:
    """Create test organization."""
    organization = Organization(name="Test Organization", building_id=test_building.id)

    phone = OrganizationPhone(phone_number="123-456-789")
    organization.phones.append(phone)

    organization.activities.append(test_activity)

    test_session.add(organization)
    await test_session.commit()
    await test_session.refresh(organization, ["building", "phones", "activities"])
    return organization


@pytest.fixture
async def test_activities_tree(test_session: AsyncSession) -> list[Activity]:
    """Create test activities tree."""
    # Level 1
    root = Activity(name="Food", level=1, parent_id=None)
    test_session.add(root)
    await test_session.flush()

    # Level 2
    child1 = Activity(name="Meat", level=2, parent_id=root.id)
    child2 = Activity(name="Dairy", level=2, parent_id=root.id)
    test_session.add_all([child1, child2])
    await test_session.flush()

    # Level 3
    grandchild = Activity(name="Beef", level=3, parent_id=child1.id)
    test_session.add(grandchild)

    await test_session.commit()

    return [root, child1, child2, grandchild]
