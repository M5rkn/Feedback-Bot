from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config.settings import settings
from database.connection import db
from database.models import FeedbackModel
from keyboards.main import get_main_keyboard, get_rating_keyboard
from aiogram.filters import CommandStart


router = Router()


class FeedbackState(StatesGroup):
    """Состояния для сбора отзыва"""
    waiting_for_message = State()
    waiting_for_rating = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для сбора обратной связи. Вы можете оставить отзыв о нашей работе.\n\n"
        "Выберите действие в меню:",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📝 Оставить отзыв")
async def start_feedback(message: Message, state: FSMContext):
    """Начало процесса оставления отзыва"""
    await state.set_state(FeedbackState.waiting_for_message)
    await message.answer(
        "📝 Напишите ваш отзыв.\n\n"
        "Расскажите, что вам понравилось или не понравилось.\n"
        "Отправьте сообщение, когда будете готовы."
    )


@router.message(FeedbackState.waiting_for_message)
async def process_message(message: Message, state: FSMContext):
    """Обработка текста отзыва"""
    await state.update_data(message=message.text)
    await state.set_state(FeedbackState.waiting_for_rating)
    await message.answer(
        "⭐️ Оцените ваш опыт от 1 до 5 звёзд.\n\n"
        "1 - Очень плохо\n"
        "5 - Отлично",
        reply_markup=get_rating_keyboard()
    )


@router.callback_query(FeedbackState.waiting_for_rating, F.data.startswith("rating_"))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора рейтинга"""
    await callback.answer()
    
    data = await state.get_data()
    rating = None if callback.data == "rating_skip" else int(callback.data.split("_")[1])
    
    # Сохранение отзыва в базу
    feedback = FeedbackModel(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        message=data["message"],
        rating=rating
    )
    
    result = await db.create_feedback(feedback)
    
    # Уведомление администраторам
    for admin_id in settings.admin_ids_list:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🔔 <b>Новый отзыв!</b>\n\n"
                f"👤 <b>От:</b> {callback.from_user.get_mention(as_html=True)}\n"
                f"🆔 ID: <code>{callback.from_user.id}</code>\n"
                f"⭐️ <b>Оценка:</b> {'⭐️' * (rating or 0)}{'-' * (5 - (rating or 5))} ({rating or 'нет'})\n\n"
                f"📝 <b>Текст:</b>\n{data['message']}\n\n"
                f"🆔 Отзыв: <code>{result['_id']}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await state.clear()
    await callback.message.answer(
        "✅ Спасибо за ваш отзыв!\n\n"
        "Мы обязательно рассмотрим его в ближайшее время.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "📊 Мои отзывы")
async def my_feedback(message: Message):
    """Просмотр своих отзывов"""
    user_feedbacks = await db.get_user_feedback(message.from_user.id)
    
    if not user_feedbacks:
        await message.answer(
            "📭 У вас пока нет отзывов.\n\n"
            "Вы можете оставить первый отзыв, выбрав «📝 Оставить отзыв»",
            reply_markup=get_main_keyboard()
        )
        return
    
    text = f"📊 <b>Ваши отзывы</b> ({len(user_feedbacks)}):\n\n"
    for i, fb in enumerate(user_feedbacks[:5], 1):
        status = "✅ Одобрено" if fb.get("is_approved") else "❌ Отклонено" if fb.get("is_approved") is False else "⏳ На проверке"
        rating = f"⭐️ {fb['rating']}/5" if fb.get('rating') else "Без оценки"
        text += f"{i}. {rating} — {status}\n"
        text += f"   «{fb['message'][:50]}...»\n\n"
    
    if len(user_feedbacks) > 5:
        text += f"... и ещё {len(user_feedbacks) - 5} отзывов"
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard())


@router.message(F.text == "ℹ️ Помощь")
async def help_command(message: Message):
    """Справка"""
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "Этот бот позволяет оставлять отзывы о нашей работе.\n\n"
        "📝 <b>Как оставить отзыв:</b>\n"
        "1. Нажмите «📝 Оставить отзыв»\n"
        "2. Напишите текст отзыва\n"
        "3. Выберите оценку от 1 до 5\n\n"
        "📊 <b>Мои отзывы</b> — просмотр ваших отзывов\n\n"
        "Администратор рассмотрит ваш отзыв в ближайшее время.",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
