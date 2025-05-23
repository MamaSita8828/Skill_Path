import os
from pydantic_settings import BaseSettings  # type: ignore
from dotenv import load_dotenv
import json

load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения."""
    # Основные настройки
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", 0))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Настройки Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    # Список администраторов (строка, парсится вручную)
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "")
     
    class Config:
        env_file = ".env"
        extra = 'allow'
        case_sensitive = True

    @property
    def admin_ids(self) -> list[int]:
        value = self.ADMIN_IDS.strip()
        if not value:
            return []
        # Пробуем как json
        try:
            ids = json.loads(value)
            if isinstance(ids, list):
                return [int(x) for x in ids]
        except Exception:
            pass
        # Иначе парсим через запятую
        return [int(x) for x in value.split(',') if x.strip().isdigit()]

settings = Settings()

if not settings.BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения") 