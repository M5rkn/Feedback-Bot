from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основное меню пользователя"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Оставить отзыв"), KeyboardButton(text="📊 Мои отзывы")],
            [KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с оценками"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐️ 1", callback_data="rating_1"),
                InlineKeyboardButton(text="⭐️ 2", callback_data="rating_2"),
                InlineKeyboardButton(text="⭐️ 3", callback_data="rating_3"),
            ],
            [
                InlineKeyboardButton(text="⭐️ 4", callback_data="rating_4"),
                InlineKeyboardButton(text="⭐️ 5", callback_data="rating_5"),
            ],
            [
                InlineKeyboardButton(text="❌ Пропустить оценку", callback_data="rating_skip")
            ]
        ]
    )
    return keyboard


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Админ-панель"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Новые отзывы"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🔍 Все отзывы"), KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_moderation_keyboard(feedback_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для модерации отзыва"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{feedback_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{feedback_id}")
            ],
            [
                InlineKeyboardButton(text="💬 Комментарий", callback_data=f"comment_{feedback_id}")
            ]
        ]
    )
    return keyboard
