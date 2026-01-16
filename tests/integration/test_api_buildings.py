import pytest
from httpx import AsyncClient

from app.models import Building


@pytest.mark.integration
class TestBuildingsAPI:
    API_KEY = "test-api-key-12345"
    BASE_URL = "/api/v1/buildings"

    async def test_get_all_buildings(self, client: AsyncClient, test_building: Building):
        """Test GET /buildings endpoint."""
        response = await client.get(self.BASE_URL, headers={"X-API-Key": self.API_KEY})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_building_by_id(self, client: AsyncClient, test_building: Building):
        """Test GET /buildings/{id} endpoint."""
        response = await client.get(
            f"{self.BASE_URL}/{test_building.id}",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_building.id
        assert data["address"] == test_building.address

    async def test_get_building_not_found(self, client: AsyncClient):
        """Test GET /buildings/{id} with non-existent ID."""
        response = await client.get(f"{self.BASE_URL}/9999", headers={"X-API-Key": self.API_KEY})

        assert response.status_code == 404

    async def test_create_building(self, client: AsyncClient):
        """Test POST /buildings endpoint."""
        building_data = {
            "address": "New Building, 1",
            "latitude": 55.7558,
            "longitude": 37.6173,
        }

        response = await client.post(
            self.BASE_URL, json=building_data, headers={"X-API-Key": self.API_KEY}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["address"] == building_data["address"]
        assert data["id"] is not None

    async def test_create_building_invalid_coordinates(self, client: AsyncClient):
        """Test POST /buildings with invalid coordinates."""
        building_data = {
            "address": "Invalid Building",
            "latitude": 100.0,  # Invalid
            "longitude": 37.6173,
        }

        response = await client.post(
            self.BASE_URL, json=building_data, headers={"X-API-Key": self.API_KEY}
        )

        assert response.status_code == 422  # Validation error

    async def test_update_building(self, client: AsyncClient, test_building: Building):
        """Test PUT /buildings/{id} endpoint."""
        update_data = {"address": "Updated Address"}

        response = await client.put(
            f"{self.BASE_URL}/{test_building.id}",
            json=update_data,
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["address"] == "Updated Address"

    async def test_delete_building(self, client: AsyncClient, test_building: Building):
        """Test DELETE /buildings/{id} endpoint."""
        response = await client.delete(
            f"{self.BASE_URL}/{test_building.id}",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 204

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test API without API key."""
        response = await client.get(self.BASE_URL)

        assert response.status_code == 401

    async def test_invalid_api_key(self, client: AsyncClient):
        """Test API with invalid API key."""
        response = await client.get(self.BASE_URL, headers={"X-API-Key": "invalid-key"})

        assert response.status_code == 403
