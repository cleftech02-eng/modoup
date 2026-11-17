from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Annotated
from config import get_settings

app = FastAPI()

settings = get_settings()

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)