from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio

from admin.admin_kb import delete_admin_kb, get_manage_access_kb, get_admin_kb
from admin.admin_orm import set_admin_status, get_admins_orm, delete_admin_orm
from admin.state import AdminStates
from user.user_orm import get_user

admin_router = Router()


@admin_router.callback_query(F.data == 'manage_access')
async def manage_access(callback: CallbackQuery):
    await callback.message.edit_text('Управление доступами', reply_markup=await get_manage_access_kb())


@admin_router.message(Command('admin_panel'))
async def manage_access_command(message: Message):
    if message.from_user.id not in [6264939461, 192659790]:
        return
    await message.answer('Управление доступами', reply_markup=await get_manage_access_kb())

@admin_router.callback_query(F.data == 'add_admin')
async def set_admin(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in [6264939461, 192659790]:
        return
    await callback.message.answer('Введите ID пользователя')
    await state.set_state(AdminStates.set_admin)

@admin_router.message(AdminStates.set_admin)
async def set_admin_id(message: Message, state: FSMContext):
    user_id = message.text
    user = await get_user(user_id)
    if user is None:
        await message.answer('Пользователь не зарегистрирован в боте')
        return
    await message.answer(f'Пользователь {user.name} - {user.tg_id}\nтеперь администратор')
    await set_admin_status(user_id, True)
    await state.clear()


@admin_router.callback_query(F.data == 'get_admins')
async def get_admins(callback: CallbackQuery):
    if callback.from_user.id not in [6264939461, 192659790]:
        return
    admins = await get_admins_orm()
    
    for admin in admins:
        
        await callback.message.answer(f'{admin.name}\n{admin.tg_id}', reply_markup=await delete_admin_kb(admin.tg_id))


@admin_router.callback_query(F.data.startswith('delete_admin_'))
async def delete_admin(callback: CallbackQuery):
    tg_id = callback.data.split('_')[-1]
    await delete_admin_orm(tg_id)
    await callback.message.edit_text(f'Администратор {tg_id} удален')
    await asyncio.sleep(1)
    await callback.message.delete()







