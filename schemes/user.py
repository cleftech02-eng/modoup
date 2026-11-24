from pydantic import BaseModel, ConfigDict, EmailStr, Field
class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    current_realm_id: int | None = None
    hp: int
    level: int

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"