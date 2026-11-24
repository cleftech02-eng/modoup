from datetime import datetime
from pydantic import BaseModel, ConfigDict
class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: str
    message: str
    created_at: datetime