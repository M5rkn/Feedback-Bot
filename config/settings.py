from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    BOT_TOKEN: str
    MONGO_URL: str = ""
    MONGODB_URI: str = ""
    ADMIN_IDS: str
    DB_NAME: str = "feedback_bot"
    
    @property
    def mongodb_connection_string(self) -> str:
        """Получить строку подключения к MongoDB"""
        # Приоритет: MONGO_URL (Railway) > MONGODB_URI > localhost
        return self.MONGO_URL or self.MONGODB_URI or "mongodb://localhost:27017"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Список ID администраторов"""
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",")]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
