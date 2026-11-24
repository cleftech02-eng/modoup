# test_db.py
from sqlalchemy import text
from database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database(), current_user, version()"))
        database, user, version = result.fetchone()

        print(" PostgreSQL connected successfully!")
        print("Database :", database)
        print("User     :", user)
        print("Version  :", version.split("\n")[0])
except Exception as e:
    print(" Database connection failed:")
    print(e)