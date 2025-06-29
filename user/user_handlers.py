
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from user.user_orm import get_user, create_user, get_free_period, decrement_free_period
from user.utils import handle_document, markdown_bold_to_html, remove_square_brackets, save_gpt_response, delete_local_file
from utils.get_yandex_gpt import yandex_gpt_async, yandex_gpt_save_vacancy
from user.user_kb import get_start_kb
from user.text_message import TextMessage
from user.states import UserStates
from datetime import datetime

from utils.upload_google_drive import upload_file
from utils.google_upload import upload_dict_to_sheet, get_last_row_number


user_router = Router()


@user_router.message(CommandStart())
async def start_command(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await create_user(message.from_user.id)
    await message.answer(TextMessage.START_MESSAGE, reply_markup=await get_start_kb())



@user_router.callback_query(F.data == 'scan_resume')
async def scan_resume(callback: CallbackQuery, state: FSMContext):
    free_period = await get_free_period(callback.from_user.id)
   
    if free_period == 0:
        await callback.message.answer('У вас закончился бесплатный период')
        return
    
    await callback.message.answer(TextMessage.SCAN_RESUME_FIRST_MESSAGE)
    await state.set_state(UserStates.scan_resume_first)

@user_router.message(UserStates.scan_resume_first)
async def scan_resume_first(message: Message, state: FSMContext, bot: Bot):
    if message.document:
        content, file_path = await handle_document(message, bot)
        print(content)
        await state.update_data(resume=content, file_path = file_path)
    else:
        await state.update_data(resume=message.text)
    await message.answer(TextMessage.SCAN_RESUME_SECOND_MESSAGE)
    await state.set_state(UserStates.scan_resume_second)

@user_router.message(UserStates.scan_resume_second)
async def scan_resume_second(message: Message, state: FSMContext):
    await state.update_data(vacancy=message.text)
    await message.answer(TextMessage.SCAN_RESUME_THIRD_MESSAGE)
    data = await state.get_data()
    resume = data.get('resume') 
    vacancy = data.get('vacancy')
    gpt_response = await yandex_gpt_async(resume, vacancy)
    await message.answer(markdown_bold_to_html(gpt_response), parse_mode='HTML')
    await start_command(message)
    await decrement_free_period(message.from_user.id)
    data_for_google_table = await yandex_gpt_save_vacancy(resume, vacancy)
    data_for_google_table = remove_square_brackets(data_for_google_table)
    name_candidate = data_for_google_table.get('ФИО')
    last_number = get_last_row_number()
    date = datetime.now().strftime('%d.%m.%Y')
    file_path_gpt, name_file_gpt = save_gpt_response(name_candidate, gpt_response, date, last_number)

    if message.from_user.username:
        tg_user = f'@{message.from_user.username}'
    else:
        tg_user = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        
    date = datetime.now().strftime('%d.%m.%Y')
    

    file_link = None
    file_link_gpt = None
    try:
        file_path = data.get('file_path')
        
        
    except:
        file_path = None
        
    if file_path:
        file_link = upload_file(file_path, f'{name_file_gpt}_CV')
        
        delete_local_file(file_path)
    if file_path_gpt:
        file_link_gpt = upload_file(file_path_gpt, f'{name_file_gpt}_Скрининг')
        delete_local_file(file_path_gpt)
        
    
    if file_link and file_link_gpt:
        data_for_google_table['Ссылка на резюме'] = str(file_link)
        data_for_google_table['Ссылка на рекомендации'] = str(file_link_gpt)
        data_for_google_table['Пользователь'] = tg_user
        data_for_google_table['Дата создания'] = date
    else:
        data_for_google_table['Ссылка на резюме'] = 'Не удалось загрузить резюме'
        data_for_google_table['Ссылка на рекомендации'] = 'Не удалось загрузить рекомендации'
        data_for_google_table['Пользователь'] = tg_user
        data_for_google_table['Дата создания'] = date
    upload_dict_to_sheet(data_for_google_table , last_number)
    
    
    
    await state.clear()
    



