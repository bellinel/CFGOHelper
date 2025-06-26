from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_admin_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Удалить', callback_data='delete_admin')
    return kb.as_markup()