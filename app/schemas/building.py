from pydantic import BaseModel, ConfigDict, Field


class BuildingBase(BaseModel):
    address: str = Field(..., max_length=500, description="Building address")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    address: str | None = Field(None, max_length=500)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class BuildingOut(BuildingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
