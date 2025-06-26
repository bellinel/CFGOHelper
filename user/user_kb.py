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
    # kb.button(text='Прислать резюме', callback_data='send_resume')
    # kb.button(text='Разместить вакансию', callback_data='post_vacancy')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)