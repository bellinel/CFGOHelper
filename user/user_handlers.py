

from aiogram import Router, F, Bot, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os
from user.user_orm import get_user, create_user, get_free_period, decrement_free_period, increment_free_period
from user.utils import handle_document, markdown_bold_to_html, remove_square_brackets, save_gpt_response, delete_local_file, send_analize_hh_text
from utils.get_yandex_gpt import yandex_gpt_async, yandex_gpt_save_vacancy
from user.user_kb import get_start_kb, get_payment_kb, payment_amount_kb, get_back_to_main_menu_kb
from user.text_message import TextMessage
from user.states import UserStates
from datetime import datetime
from utils.upload_google_drive import upload_file_async
from utils.google_upload import upload_dict_to_sheet, get_last_row_number, append_row_to_billing_sheet
from admin.admin_kb import get_admin_kb, get_super_admin_kb
from dotenv import load_dotenv
import json
load_dotenv()

user_router = Router()
CHANNEL_ID = os.getenv('CHANNEL_ID')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')


ADMIN_ID = os.getenv('ADMIN_ID').split(',')
ADMIN_ID = [int(id) for id in ADMIN_ID]

BILLING_ID = os.getenv('BILLING_ID')




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
    
    user = await get_user(int(message.from_user.id))
    if user is None:
        if message.from_user.username:
            name = f'@{message.from_user.username}'
        else:
            name = message.from_user.first_name

        await message.answer('Пожалуйста подождите, мы создаем ваш аккаунт')
        new_user = await create_user(int(message.from_user.id), name)
        time = datetime.now().strftime('%H:%M')
        date = datetime.now().strftime('%d.%m.%Y')
        date_time = f'{date} {time}'
        try:
            name = new_user.name
        except:
            return
        service = '-'
        operation = 'Новый пользователь'
        count = '-'
        balance = new_user.free_period
        last_number = await get_last_row_number(BILLING_ID)
        data_for_billing_sheet = {
            '№': last_number+1,
            'Дата и время': date_time,
            'Имя пользователя': name,
            'Услуга': service,
            'Операция': operation,
            'Количество': count,
            'Баланс': balance}
        await append_row_to_billing_sheet(BILLING_ID, 'Лист1', data_for_billing_sheet)
    
    if message.from_user.id in ADMIN_ID:
        await message.answer(TextMessage.START_MESSAGE, reply_markup=await get_super_admin_kb())
        return
    
    if user and user.is_admin:
        await message.answer(TextMessage.START_MESSAGE, reply_markup=await get_admin_kb())
        return
    
    await message.answer(TextMessage.START_MESSAGE, reply_markup=await get_start_kb())


@user_router.callback_query(F.data == 'scan_resume')
async def scan_resume(callback: CallbackQuery, state: FSMContext):
    free_period = await get_free_period(int(callback.from_user.id))
    user = await get_user(int(callback.from_user.id))
    if user and not user.is_admin and not user.is_vip and callback.from_user.id not in ADMIN_ID:
        if free_period == 0:
            
            await callback.answer('У вас закончились бесплатные попытки, вам необходимо купить новый пакет Скрининга', show_alert=True)
            await payment_menu(callback)
            return
    
    
    await callback.message.edit_text(TextMessage.SCAN_RESUME_FIRST_MESSAGE, reply_markup=await get_back_to_main_menu_kb())
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
    user = await get_user(int(message.from_user.id))
    if user and not user.is_admin and not user.is_vip and message.from_user.id not in ADMIN_ID:
        await decrement_free_period(int(message.from_user.id))
        
    data_for_google_table = await yandex_gpt_save_vacancy(resume, vacancy)
    data_for_google_table = remove_square_brackets(data_for_google_table)
    name_candidate = data_for_google_table.get('ФИО')
    last_number = await get_last_row_number(BILLING_ID)
    
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
        file_link = await upload_file_async(file_path, f'{name_file_gpt}_CV')
        
        delete_local_file(file_path)
    if file_path_gpt:
        file_link_gpt = await upload_file_async(file_path_gpt, f'{name_file_gpt}_Скрининг')
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
        
    await upload_dict_to_sheet(data_for_google_table ,last_number)
    date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
    data_for_billing_sheet = {
        '№': last_number+1,
        'Дата и время': date_time,
        'Имя пользователя': user.name,
        'Услуга': 'Скрининг',
        'Операция': 'Списание',
        'Количество': 1,
        'Баланс': user.free_period-1}
    await append_row_to_billing_sheet(BILLING_ID, 'Лист1', data_for_billing_sheet)
    
    
    await state.clear()
    

@user_router.callback_query(F.data == 'back_to_main_menu')
async def back_to_main_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if callback.from_user.id in ADMIN_ID:
        await callback.message.edit_text(TextMessage.START_MESSAGE, reply_markup=await get_super_admin_kb())
    elif user and user.is_admin:
        await callback.message.edit_text(TextMessage.START_MESSAGE, reply_markup=await get_admin_kb())
    else:
        await callback.message.edit_text(TextMessage.START_MESSAGE, reply_markup=await get_start_kb())


@user_router.callback_query(F.data == 'payment')
async def payment_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
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
    await callback.message.edit_text(f'Вы выбрали {amount} пакетов', reply_markup=await payment_amount_kb(amount, price))



    
@user_router.callback_query(F.data.startswith('start_payment_'))
async def payment_amount_callback(callback: CallbackQuery, bot: Bot):
    amount = int(callback.data.split('_')[-2])
    price = int(callback.data.split('_')[-1])
    print(f"{price:.2f}")
    await callback.message.delete()
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title='Покупка пакетов',
        need_email=True,
        send_email_to_provider=True,
        description=f'Покупка {amount} пакетов',
        payload=json.dumps({'amount': amount, 'price': price}),
        provider_token=PROVIDER_TOKEN,
        
        currency='RUB',
        prices=[
            LabeledPrice(
                label=f'{amount} пакетов',
                amount=price * 100
            )
        ],
        is_flexible=False,
        provider_data=json.dumps({
  "receipt": {
    "items": [
      {
        "description": "Покупка пакетов",
        "quantity": 1,
        "amount": {
          "value": f"{price:.2f}",
          "currency": "RUB"
        },
        "vat_code": 1,
        "payment_mode": "full_payment",
        "payment_subject": "service"
      }
    ]
  }
}))

    await callback.answer()
    
    
@user_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    
    
@user_router.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message, bot: Bot):
    # ✅ Распаковываем строку обратно в словарь
    
    payload_data = json.loads(message.successful_payment.invoice_payload)
    
    amount = payload_data.get('amount')  # Кол-во пакетов
    price = payload_data.get('price')    # Стоимость
    
    print(f"✅ Успешная оплата: {price}₽ за {amount} пакетов")

    await increment_free_period(int(message.from_user.id), amount)
    await message.answer(
        f"Спасибо за оплату! Вам начислено {amount} скринингов.",
        reply_markup=await get_back_to_main_menu_kb()
    )
    user = await get_user(message.from_user.id)
    last_number = await get_last_row_number(BILLING_ID)
    date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
    data_for_billing_sheet = {
        '№': last_number+1,
        'Дата и время': date_time,
        'Имя пользователя': user.name,
        'Услуга': 'Скрининг',
        'Операция': 'Пополнение',
        'Количество': amount,
        'Баланс': user.free_period}
    await append_row_to_billing_sheet(BILLING_ID, 'Лист1', data_for_billing_sheet)