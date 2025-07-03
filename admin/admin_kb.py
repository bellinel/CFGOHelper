from aiogram.utils.keyboard import InlineKeyboardBuilder


async def delete_admin_kb(tg_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text='Убрать права админа', callback_data=f'delete_admin_{tg_id}')
    return kb.as_markup()

async def get_admin_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Сканировать резюме', callback_data='scan_resume')
    kb.button(text='Оплата услуг', callback_data='payment')
    kb.button(text='Управление VIP пользователями', callback_data='manage_vip_users')
    kb.adjust(1)
    return kb.as_markup()


async def get_manage_admins_kb():
    '''
    Клавиатура для управления доступом
    Добавить админа - каллбэк add_admin
    Показать список админов - каллбэк get_admins
    '''
    kb = InlineKeyboardBuilder()
    kb.button(text='Добавить админа', callback_data='add_admin')
    kb.button(text='Показать список админов', callback_data='get_admins')
    kb.button(text='Назад', callback_data='back_to_main_menu')
    kb.adjust(1)
    return kb.as_markup()


async def get_super_admin_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Сканировать резюме', callback_data='scan_resume')
    kb.button(text='Оплата услуг', callback_data='payment')
    kb.button(text='Управление VIP пользователями', callback_data='manage_vip_users')
    kb.button(text='Управление админами', callback_data='manage_admins')
    kb.adjust(1)
    return kb.as_markup()


async def get_manage_vip_users_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Показать список VIP пользователей', callback_data='get_vip_users')
    kb.button(text='Добавить VIP пользователя', callback_data='add_vip')
    kb.button(text='Назад', callback_data='back_to_main_menu')
    kb.adjust(1)
    return kb.as_markup()


async def delete_vip_kb(tg_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text='Убрать VIP статус', callback_data=f'delete_vip_{tg_id}')
    return kb.as_markup()