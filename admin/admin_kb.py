from aiogram.utils.keyboard import InlineKeyboardBuilder


async def delete_admin_kb(tg_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text='Убрать права админа', callback_data=f'delete_admin_{tg_id}')
    return kb.as_markup()

async def get_admin_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Сканировать резюме', callback_data='scan_resume')
    kb.button(text='Управление доступами', callback_data='manage_access')
    kb.button(text='Оплата услуг', callback_data='payment')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


async def get_manage_access_kb():
    '''
    Клавиатура для управления доступом
    Добавить админа - каллбэк add_admin
    Показать список админов - каллбэк get_admins
    '''
    kb = InlineKeyboardBuilder()
    kb.button(text='Добавить админа', callback_data='add_admin')
    kb.button(text='Показать список админов', callback_data='get_admins')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


