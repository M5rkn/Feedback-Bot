from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from config.settings import settings
from database.models import FeedbackModel
from datetime import datetime


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Подключение к MongoDB"""
        uri = settings.mongodb_connection_string
        
        # Railway сам управляет SSL параметрами в своей переменной
        # Не добавляем ничего дополнительно
        
        self.client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        
        # Проверка подключения
        await self.client.admin.command('ping')
        self.db = self.client[settings.DB_NAME]
        print(f"✅ Подключено к MongoDB: {settings.DB_NAME}")
    
    async def disconnect(self):
        """Отключение от MongoDB"""
        if self.client:
            self.client.close()
            print("🔌 Отключено от MongoDB")
    
    async def create_feedback(self, feedback: FeedbackModel) -> dict:
        """Создание нового отзыва"""
        collection = self.db.feedback
        doc = feedback.model_dump()
        result = await collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc
    
    async def get_all_feedback(self, limit: int = 50):
        """Получение всех отзывов"""
        collection = self.db.feedback
        cursor = collection.find().sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_pending_feedback(self):
        """Получение отзывов на модерации"""
        collection = self.db.feedback
        cursor = collection.find({"is_moderated": False}).sort("created_at", -1)
        return await cursor.to_list(length=100)
    
    async def approve_feedback(self, feedback_id: str, admin_comment: str = None):
        """Одобрение отзыва"""
        collection = self.db.feedback
        await collection.update_one(
            {"_id": feedback_id},
            {"$set": {
                "is_moderated": True,
                "is_approved": True,
                "admin_comment": admin_comment,
                "moderated_at": datetime.now()
            }}
        )
    
    async def reject_feedback(self, feedback_id: str, admin_comment: str = None):
        """Отклонение отзыва"""
        collection = self.db.feedback
        await collection.update_one(
            {"_id": feedback_id},
            {"$set": {
                "is_moderated": True,
                "is_approved": False,
                "admin_comment": admin_comment,
                "moderated_at": datetime.now()
            }}
        )
    
    async def get_feedback_stats(self):
        """Получение статистики по отзывам"""
        collection = self.db.feedback
        total = await collection.count_documents({})
        moderated = await collection.count_documents({"is_moderated": True})
        approved = await collection.count_documents({"is_approved": True})
        rejected = await collection.count_documents({"is_approved": False})
        pending = await collection.count_documents({"is_moderated": False})
        
        return {
            "total": total,
            "moderated": moderated,
            "approved": approved,
            "rejected": rejected,
            "pending": pending
        }
    
    async def get_user_feedback(self, user_id: int):
        """Получение отзывов пользователя"""
        collection = self.db.feedback
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=100)


db = Database()
