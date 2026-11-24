from pydantic import BaseModel

from schemes.realm import RealmOut


class ProfileOut(BaseModel):
    id: int
    full_name: str
    email: str
    realm: RealmOut | None = None
    hp: int
    level: int
    completed_lessons: int
    realm_total_lessons: int
    realm_completed_lessons: int
    realm_progress_percent: int