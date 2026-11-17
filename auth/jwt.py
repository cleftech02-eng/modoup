from config import get_settings

settings = get_settings()

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)