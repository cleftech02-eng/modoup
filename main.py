
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import auth, realm, lesson, profile, activity

settings = get_settings()

app = FastAPI()

# Temporary development and deployment configuration.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(realm.router)
app.include_router(lesson.router)
app.include_router(profile.router)
app.include_router(activity.router)


@app.get("/")
def root():
    return {"message": "Welcome to Modo Up API"}
