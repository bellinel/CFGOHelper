

from aiogram import Router, F, Bot, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os
from user.user_orm import get_user, create_user, get_free_period, decrement_free_period, increment_free_period
from user.utils import handle_document, markdown_bold_to_html, remove_square_brackets, save_gpt_response, delete_local_file, send_analize_hh_text
from utils.get_yandex_gpt import yandex_gpt_async, yandex_gpt_save_vacancy
from user.user_kb import get_start_kb, get_payment_kb, payment_amount_kb
from user.text_message import TextMessage
from user.states import UserStates
from datetime import datetime
from utils.upload_google_drive import upload_file
from utils.google_upload import upload_dict_to_sheet, get_last_row_number
from admin.admin_kb import get_admin_kb
from dotenv import load_dotenv

load_dotenv()

user_router = Router()
CHANNEL_ID = os.getenv('CHANNEL_ID')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')
print(PROVIDER_TOKEN)

@user_router.message(Command('start'))
async def start_command(message: Message, state: FSMContext):

    await state.clear()
    await message.answer(TextMessage.ON_START_MESSAGE)



@user_router.message(Command('main_menu'))
async def start_command(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
    if member.status not in ["member", "administrator", "creator"]:
        await message.answer(TextMessage.CHANNEL_MESSAGE)
        return
    
    user = await get_user(message.from_user.id)
    if user is None:
        if message.from_user.username:
            name = f'@{message.from_user.username}'
        else:
            name = message.from_user.first_name
        await create_user(message.from_user.id, name)
        
    if user and user.is_admin:
        await message.answer(TextMessage.START_MESSAGE, reply_markup=await get_admin_kb())
        return
    await message.answer(TextMessage.START_MESSAGE, reply_markup=await get_start_kb())



@user_router.callback_query(F.data == 'scan_resume')
async def scan_resume(callback: CallbackQuery, state: FSMContext):
    free_period = await get_free_period(callback.from_user.id)
    user = await get_user(callback.from_user.id)
    if user and not user.is_admin:
        if free_period == 0:
            await callback.message.answer('у вас закончились бесплатные попытки, вам необходимо купить новый пакет Скрининга')
            await payment_menu(callback)
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
    if message.text.startswith('https://hh.ru/vacancy/'):
        url = message.text
        
        text_vacancy = await send_analize_hh_text(url, message)

        if text_vacancy:
            print(text_vacancy)
            
            await state.update_data(vacancy=text_vacancy, url=url)
        else:
            await message.answer('Не удалось получить текст вакансии, попробуйте ввести текст вакансии вручную')
            return
    else:
        
        await state.update_data(vacancy=message.text, url = None)
    await message.answer(TextMessage.SCAN_RESUME_THIRD_MESSAGE)

    data = await state.get_data()
    resume = data.get('resume') 
    vacancy = data.get('vacancy')
    url = data.get('url')
    gpt_response = await yandex_gpt_async(resume, vacancy)
    await message.answer(markdown_bold_to_html(gpt_response), parse_mode='HTML')
    user = await get_user(message.from_user.id)
    if user and not user.is_admin:
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
        if url:
            data_for_google_table['Вакансия'] = url
        else:
            data_for_google_table['Вакансия'] = vacancy
        data_for_google_table['Ссылка на резюме'] = str(file_link)
        data_for_google_table['Ссылка на рекомендации'] = str(file_link_gpt)
        data_for_google_table['Пользователь'] = tg_user
        data_for_google_table['Дата создания'] = date
        
    else:
        if url:
            data_for_google_table['Вакансия'] = url
        else:
            data_for_google_table['Вакансия'] = vacancy
        data_for_google_table['Ссылка на резюме'] = 'Не удалось загрузить резюме'
        data_for_google_table['Ссылка на рекомендации'] = 'Не удалось загрузить рекомендации'
        data_for_google_table['Пользователь'] = tg_user
        data_for_google_table['Дата создания'] = date
        
    upload_dict_to_sheet(data_for_google_table ,last_number)
    
    
    
    await state.clear()
    


@user_router.callback_query(F.data == 'payment')
async def payment_menu(callback: CallbackQuery):
    await callback.message.edit_text(TextMessage.PAYMENT_MESSAGE, reply_markup=await get_payment_kb())


@user_router.callback_query(F.data.startswith('payment_'))
async def payment_amount(callback: CallbackQuery):
    amount = callback.data.split('_')[1]
    if amount == '5':
        price = 500
    elif amount == '10':
        price = 750
    elif amount == '20':
        price = 1200
    elif amount == '50':
        price = 2500
    await callback.message.edit_text(f'Вы выбрали {amount} пакетов', reply_markup=await payment_amount_kb(price))



    
# @user_router.callback_query(F.data.startswith('start_payment_'))
# async def payment_amount_callback(callback: CallbackQuery, bot: Bot):
#     amount = int(callback.data.split('_')[-1])
#     await bot.send_invoice(
#         chat_id=callback.from_user.id,
#         title='Покупка пакетов',
#         description=f'Покупка {amount} пакетов',
#         payload=f'payment_{amount}_packages',
#         provider_token=PROVIDER_TOKEN,
#         currency='RUB',
#         prices=[
#             LabeledPrice(
#                 label=f'{amount} пакетов',
#                 amount=amount * 250 * 100
#             )
#         ]
#     )
#     await callback.answer()
    
    
# @user_router.pre_checkout_query(lambda query: True)
# async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    
    
# @user_router.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
# async def successful_payment(message: Message):
#     amount = message.successful_payment.total_amount // 100
#     print(f"✅ Успешная оплата: {amount}₽")
#     packages = amount // 250
#     await increment_free_period(message.from_user.id, packages)
#     await message.answer("Спасибо за оплату!")