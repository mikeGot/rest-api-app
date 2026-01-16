import asyncio

from app.core.database import AsyncSessionLocal, Base, engine
from app.models import Activity, Building, Organization, OrganizationPhone


async def seed_data():
    """Seed database with test data"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        result = await session.execute(select(Building))
        if result.scalar_one_or_none():
            print("Data already exists, skipping seed")
            return

        buildings = [
            Building(
                address="г. Москва, ул. Тверская 1, офис 3", latitude=55.7558, longitude=37.6173
            ),
            Building(
                address="г. Санкт-Петербург, Невский проспект 28",
                latitude=59.9343,
                longitude=30.3351,
            ),
            Building(
                address="г. Новосибирск, ул. Блюхера 32/1", latitude=55.0084, longitude=82.9357
            ),
            Building(
                address="г. Екатеринбург, ул. Малышева 51", latitude=56.8389, longitude=60.6057
            ),
        ]

        for building in buildings:
            session.add(building)

        await session.flush()

        # Level 1
        food = Activity(name="Еда", level=1, parent_id=None)
        automobiles = Activity(name="Автомобили", level=1, parent_id=None)
        session.add_all([food, automobiles])
        await session.flush()

        # Level 2
        meat = Activity(name="Мясная продукция", level=2, parent_id=food.id)
        dairy = Activity(name="Молочная продукция", level=2, parent_id=food.id)
        trucks = Activity(name="Грузовые", level=2, parent_id=automobiles.id)
        cars = Activity(name="Легковые", level=2, parent_id=automobiles.id)
        session.add_all([meat, dairy, trucks, cars])
        await session.flush()

        # Level 3
        parts = Activity(name="Запчасти", level=3, parent_id=cars.id)
        accessories = Activity(name="Аксессуары", level=3, parent_id=cars.id)
        session.add_all([parts, accessories])
        await session.flush()

        orgs_data = [
            {
                "name": 'ООО "Рога и Копыта"',
                "building": buildings[0],
                "phones": ["2-222-222", "3-333-333", "8-923-666-13-13"],
                "activities": [meat, dairy],
            },
            {
                "name": 'ЗАО "Мясокомбинат"',
                "building": buildings[1],
                "phones": ["812-555-01-01"],
                "activities": [meat],
            },
            {
                "name": 'ИП "Молочные продукты"',
                "building": buildings[0],
                "phones": ["495-123-45-67", "495-123-45-68"],
                "activities": [dairy],
            },
            {
                "name": 'ООО "АвтоЗапчасти Сибирь"',
                "building": buildings[2],
                "phones": ["383-222-33-44"],
                "activities": [parts, accessories],
            },
            {
                "name": 'ООО "ГрузАвто"',
                "building": buildings[3],
                "phones": ["343-555-77-88", "343-555-77-89"],
                "activities": [trucks],
            },
            {
                "name": 'Автосалон "Премиум"',
                "building": buildings[1],
                "phones": ["812-900-00-01"],
                "activities": [cars, accessories],
            },
        ]

        for org_data in orgs_data:
            org = Organization(name=org_data["name"], building_id=org_data["building"].id)  # type: ignore[attr-defined]

            for phone_number in org_data["phones"]:  # type: ignore[attr-defined]
                phone = OrganizationPhone(phone_number=phone_number)
                org.phones.append(phone)

            for activity in org_data["activities"]:  # type: ignore[attr-defined]
                org.activities.append(activity)

            session.add(org)

        await session.commit()

        print("✅ Seed data created successfully!")
        print(f"   - {len(buildings)} buildings")
        print(f"   - {8} activities (3-level tree)")
        print(f"   - {len(orgs_data)} organizations")


if __name__ == "__main__":
    asyncio.run(seed_data())
