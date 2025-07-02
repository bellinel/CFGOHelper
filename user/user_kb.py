from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_start_kb():

    '''
    Клавиатура для стартового меню
    Сканирование резюме - каллбэк scan_resume
    Прислать резюме - каллбэк send_resume
    Разместить вакансию - каллбэк post_vacancy
    '''
    kb = InlineKeyboardBuilder()
    kb.button(text='Сканировать резюме', callback_data='scan_resume')
    kb.button(text='Оплата услуг', callback_data='payment')
    # kb.button(text='Прислать резюме', callback_data='send_resume')
    # kb.button(text='Разместить вакансию', callback_data='post_vacancy')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)



async def get_payment_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='5 скринингов - 500 р.', callback_data='payment_5')
    kb.button(text='10 скринингов - 750 р.', callback_data='payment_10')
    kb.button(text='20 скринингов - 1200 р.', callback_data='payment_20')
    kb.button(text='50 скринингов - 2500 р.', callback_data='payment_50')
    kb.button(text='Назад', callback_data='back_to_main_menu')
    
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)



async def payment_amount_kb(amount: int):
    kb = InlineKeyboardBuilder()
    kb.button(text='Оплатить', callback_data=f'start_payment_{amount}')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)



async def get_back_to_main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='back_to_main_menu')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)



