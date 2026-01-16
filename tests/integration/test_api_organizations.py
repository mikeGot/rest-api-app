import pytest
from httpx import AsyncClient

from app.models import Activity, Building, Organization


@pytest.mark.integration
class TestOrganizationsAPI:
    API_KEY = "test-api-key-12345"
    BASE_URL = "/api/v1/organizations"

    async def test_get_all_organizations(
        self, client: AsyncClient, test_organization: Organization
    ):
        """Test GET /organizations endpoint."""
        response = await client.get(self.BASE_URL, headers={"X-API-Key": self.API_KEY})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_organizations_by_building(
        self, client: AsyncClient, test_organization: Organization
    ):
        """Test GET /organizations with building filter."""
        response = await client.get(
            f"{self.BASE_URL}?building_id={test_organization.building_id}",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(org["building_id"] == test_organization.building_id for org in data)

    async def test_get_organization_by_id(
        self, client: AsyncClient, test_organization: Organization
    ):
        """Test GET /organizations/{id} endpoint."""
        response = await client.get(
            f"{self.BASE_URL}/{test_organization.id}",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_organization.id
        assert data["name"] == test_organization.name
        assert "building" in data
        assert "phones" in data
        assert "activities" in data

    async def test_search_organizations_by_name(
        self, client: AsyncClient, test_organization: Organization
    ):
        """Test GET /organizations/search?name endpoint."""
        response = await client.get(
            f"{self.BASE_URL}/search?name=Test",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_search_without_params(self, client: AsyncClient):
        """Test GET /organizations/search without parameters."""
        response = await client.get(f"{self.BASE_URL}/search", headers={"X-API-Key": self.API_KEY})

        assert response.status_code == 400

    async def test_create_organization(
        self,
        client: AsyncClient,
        test_building: Building,
        test_activity: Activity,
    ):
        """Test POST /organizations endpoint."""
        org_data = {
            "name": "New Organization",
            "building_id": test_building.id,
            "phone_numbers": ["111-222-333", "444-555-666"],
            "activity_ids": [test_activity.id],
        }

        response = await client.post(
            self.BASE_URL, json=org_data, headers={"X-API-Key": self.API_KEY}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == org_data["name"]
        assert len(data["phones"]) == 2
        assert len(data["activities"]) == 1

    async def test_update_organization(self, client: AsyncClient, test_organization: Organization):
        """Test PUT /organizations/{id} endpoint."""
        update_data = {
            "name": "Updated Organization",
            "phone_numbers": ["999-888-777"],
        }

        response = await client.put(
            f"{self.BASE_URL}/{test_organization.id}",
            json=update_data,
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Organization"
        assert len(data["phones"]) == 1

    async def test_delete_organization(self, client: AsyncClient, test_organization: Organization):
        """Test DELETE /organizations/{id} endpoint."""
        response = await client.delete(
            f"{self.BASE_URL}/{test_organization.id}",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(
            f"{self.BASE_URL}/{test_organization.id}",
            headers={"X-API-Key": self.API_KEY},
        )
        assert get_response.status_code == 404

    async def test_pagination(self, client: AsyncClient, test_organization: Organization):
        """Test pagination parameters."""
        response = await client.get(
            f"{self.BASE_URL}?skip=0&limit=1",
            headers={"X-API-Key": self.API_KEY},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
