from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FeedbackModel(BaseModel):
    """Модель отзыва"""
    
    user_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    message: str
    rating: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_moderated: bool = False
    is_approved: Optional[bool] = None
    admin_comment: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
