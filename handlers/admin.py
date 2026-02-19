from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config.settings import settings
from database.connection import db
from keyboards.main import get_admin_keyboard, get_moderation_keyboard
from aiogram.filters import Command


router = Router()


class AdminState(StatesGroup):
    """Состояния для админ-панели"""
    waiting_for_comment = State()


def is_admin(user_id: int) -> bool:
    """Проверка на администратора"""
    return user_id in settings.admin_ids_list


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Админ-панель"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🛠 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


@router.message(F.text == "📋 Новые отзывы")
async def new_feedback(message: Message):
    """Просмотр новых отзывов"""
    if not is_admin(message.from_user.id):
        return
    
    pending = await db.get_pending_feedback()
    
    if not pending:
        await message.answer("✅ Все отзывы обработаны!\n\nНовых отзывов нет.")
        return
    
    for fb in pending[:10]:  # Максимум 10 за раз
        rating = f"⭐️ {fb['rating']}/5" if fb.get('rating') else "Без оценки"
        await message.answer(
            f"🔔 <b>Новый отзыв</b>\n\n"
            f"👤 <b>От:</b> @{fb.get('username', 'нет')} / {fb['first_name']}\n"
            f"🆔 ID: <code>{fb['user_id']}</code>\n"
            f"{rating}\n\n"
            f"📝 <b>Текст:</b>\n{fb['message']}\n\n"
            f"🆔 <code>{fb['_id']}</code>",
            parse_mode="HTML",
            reply_markup=get_moderation_keyboard(fb['_id'])
        )


@router.message(F.text == "📊 Статистика")
async def stats_command(message: Message):
    """Статистика отзывов"""
    if not is_admin(message.from_user.id):
        return
    
    stats = await db.get_feedback_stats()
    
    text = (
        "📊 <b>Статистика отзывов</b>\n\n"
        f"📝 Всего: {stats['total']}\n"
        f"✅ Одобрено: {stats['approved']}\n"
        f"❌ Отклонено: {stats['rejected']}\n"
        f"⏳ На проверке: {stats['pending']}\n\n"
        f"📈 Процент одобрения: "
        f"{round(stats['approved'] / stats['moderated'] * 100) if stats['moderated'] > 0 else 0}%"
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_keyboard())


@router.message(F.text == "🔍 Все отзывы")
async def all_feedback(message: Message):
    """Все отзывы"""
    if not is_admin(message.from_user.id):
        return
    
    feedbacks = await db.get_all_feedback(limit=20)
    
    if not feedbacks:
        await message.answer("📭 Пока нет отзывов.")
        return
    
    for fb in feedbacks[:5]:
        status = "✅" if fb.get("is_approved") else "❌" if fb.get("is_approved") is False else "⏳"
        rating = f"⭐️ {fb['rating']}/5" if fb.get('rating') else "Без оценки"
        await message.answer(
            f"{status} <b>Отзыв</b>\n\n"
            f"👤 @{fb.get('username', 'нет')} / {fb['first_name']}\n"
            f"{rating}\n\n"
            f"📝 {fb['message'][:200]}{'...' if len(fb['message']) > 200 else ''}\n\n"
            f"🆔 <code>{fb['_id']}</code>",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("approve_"))
async def approve_feedback(callback: CallbackQuery):
    """Одобрение отзыва"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    feedback_id = callback.data.split("_")[1]
    await db.approve_feedback(feedback_id)
    
    await callback.answer("✅ Отзыв одобрен!")
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Уведомление пользователю
    try:
        # Нужно получить user_id из отзыва
        pass  # Можно доработать
    except Exception:
        pass


@router.callback_query(F.data.startswith("reject_"))
async def reject_feedback(callback: CallbackQuery):
    """Отклонение отзыва"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    feedback_id = callback.data.split("_")[1]
    await db.reject_feedback(feedback_id)
    
    await callback.answer("❌ Отзыв отклонён")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("comment_"))
async def add_comment(callback: CallbackQuery, state: FSMContext):
    """Добавление комментария к отзыву"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет прав", show_alert=True)
        return
    
    feedback_id = callback.data.split("_")[1]
    await state.update_data(feedback_id=feedback_id)
    await state.set_state(AdminState.waiting_for_comment)
    
    await callback.answer("Напишите комментарий к отзыву")
    await callback.message.answer("💬 Введите комментарий:")


@router.message(AdminState.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    """Обработка комментария"""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    feedback_id = data.get("feedback_id")
    
    if feedback_id:
        await db.approve_feedback(feedback_id, message.text)
        await message.answer("✅ Комментарий добавлен!")
    
    await state.clear()


@router.message(F.text == "🔙 Главное меню")
async def back_to_main(message: Message):
    """Возврат в главное меню"""
    if not is_admin(message.from_user.id):
        return
    
    from keyboards.main import get_main_keyboard
    await message.answer(
        "🔙 Возврат в главное меню",
        reply_markup=get_main_keyboard()
    )
