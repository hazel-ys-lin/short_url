import os


class Config:
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", "*")
    DB_NAME: str = os.getenv("DB_NAME", "database")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:8000")
    RATE_LIMIT_PER_MINUTE: int = os.getenv("RATE_LIMIT_PER_MINUTE", 5)
