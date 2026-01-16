from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActivityBase(BaseModel):
    name: str = Field(..., max_length=200, description="Activity name")
    parent_id: int | None = Field(None, description="Parent activity ID for tree structure")


class ActivityCreate(ActivityBase):
    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, v: int | None) -> int | None:
        return v


class ActivityUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    parent_id: int | None = None


class ActivityOut(ActivityBase):
    id: int
    level: int = Field(..., ge=1, le=3, description="Nesting level (1-3)")

    model_config = ConfigDict(from_attributes=True)


class ActivityTree(ActivityOut):
    children: list["ActivityTree"] = []

    model_config = ConfigDict(from_attributes=True)
