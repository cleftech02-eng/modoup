from pydantic import BaseModel, ConfigDict


class RealmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None


class RealmSelect(BaseModel):
    realm_id: int