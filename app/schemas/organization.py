from pydantic import BaseModel, ConfigDict, Field

from app.schemas.activity import ActivityOut
from app.schemas.building import BuildingOut


class OrganizationPhoneBase(BaseModel):
    phone_number: str = Field(..., max_length=20, description="Phone number")


class OrganizationPhoneCreate(OrganizationPhoneBase):
    pass


class OrganizationPhoneOut(OrganizationPhoneBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=300, description="Organization name")
    building_id: int = Field(..., description="Building ID where organization is located")


class OrganizationCreate(OrganizationBase):
    phone_numbers: list[str] = Field(default_factory=list, description="List of phone numbers")
    activity_ids: list[int] = Field(default_factory=list, description="List of activity IDs")


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, max_length=300)
    building_id: int | None = None
    phone_numbers: list[str] | None = None
    activity_ids: list[int] | None = None


class OrganizationOut(OrganizationBase):
    id: int
    phones: list[OrganizationPhoneOut] = []
    activities: list[ActivityOut] = []
    building: BuildingOut

    model_config = ConfigDict(from_attributes=True)


class OrganizationListOut(BaseModel):
    id: int
    name: str
    building: BuildingOut

    model_config = ConfigDict(from_attributes=True)
