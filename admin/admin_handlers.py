from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio

from admin.admin_orm import set_admin_status, get_admins_orm, delete_admin_orm
from admin.admin_kb import get_admin_kb
from admin.state import AdminStates

admin_router = Router()

@admin_router.message(Command('set_admin'))
async def set_admin(message: Message, state: FSMContext):
    if message.from_user.id not in [6264939461, 192659790]:
        return
    await message.answer('Введите ID пользователя')
    await state.set_state(AdminStates.set_admin)

@admin_router.message(AdminStates.set_admin)
async def set_admin_id(message: Message, state: FSMContext):
    user_id = message.text
    await message.answer(f'Пользователь {user_id} теперь администратор')
    await set_admin_status(user_id, True)
    await state.clear()


@admin_router.message(Command('get_admins'))
async def get_admins(message: Message):
    if message.from_user.id not in [6264939461, 192659790]:
        return
    admins = await get_admins_orm()
    for admin in admins:
        await message.answer(f'{admin.tg_id}', reply_markup=await get_admin_kb())


@admin_router.callback_query(F.data == 'delete_admin')
async def delete_admin(callback: CallbackQuery):
    tg_id = callback.message.text
    await delete_admin_orm(tg_id)
    await callback.message.edit_text(f'Администратор {tg_id} удален')
    await asyncio.sleep(1)
    await callback.message.delete()
