import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from user.user_orm import get_user, create_user, get_free_period, decrement_free_period
from user.utils import read_txt, read_docx, read_pdf, markdown_bold_to_html
from utils.get_yandex_gpt import yandex_gpt_async
from user.user_kb import get_start_kb
from user.text_message import TextMessage
from user.states import UserStates



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
        content = await handle_document(message, bot)
        print(content)
        await state.update_data(resume=content)
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
    await message.answer(markdown_bold_to_html(await yandex_gpt_async(resume, vacancy)), parse_mode='HTML')
    free_period = await decrement_free_period(message.from_user.id)
    if free_period is None:
        await message.answer('У вас закончился бесплатный период')
        return
    await state.clear()
    


async def handle_document(msg: Message, bot: Bot):
    file_info = await bot.get_file(msg.document.file_id)
    file_path = file_info.file_path
    file_name = msg.document.file_name
    ext = file_name.split('.')[-1].lower()

    save_path = f"downloads/{file_name}"
    os.makedirs("downloads", exist_ok=True)

    await bot.download_file(file_path, destination=save_path)

    try:
        if ext == "txt":
            content = await read_txt(save_path)
        elif ext == "docx":
            content = await read_docx(save_path)
        elif ext == "pdf":
            content = await read_pdf(save_path)
        else:
            await msg.answer("❌ Поддерживаются только .txt, .docx и .pdf файлы.")
            return
        return content
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
