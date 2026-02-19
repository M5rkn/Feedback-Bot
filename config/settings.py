from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    BOT_TOKEN: str
    MONGODB_URI: str = "mongodb://localhost:27017"
    ADMIN_IDS: str
    DB_NAME: str = "feedback_bot"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Список ID администраторов"""
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",")]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
