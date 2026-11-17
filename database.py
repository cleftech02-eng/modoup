from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import get_settings

settings = get_settings()


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Checks if connection is alive before using it
    pool_size=5,                 # Good for free-tier online DBs
    max_overflow=10,
    echo=settings.DEBUG          # Shows SQL queries when DEBUG=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()