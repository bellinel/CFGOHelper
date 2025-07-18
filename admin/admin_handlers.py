from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio

from admin.admin_kb import admin_kb, delete_admin_kb, get_manage_admins_kb, get_manage_vip_users_kb, delete_vip_kb, get_admin_kb, get_super_admin_kb
from admin.admin_orm import set_admin_status, get_admins_orm, delete_admin_orm, get_vip_users_orm, delete_vip_orm, set_vip_status
from admin.state import AdminStates
from user.user_orm import get_user
from user.text_message import TextMessage
import os
from dotenv import load_dotenv

load_dotenv()

admin_router = Router()

ADMIN_ID = os.getenv('ADMIN_ID').split(',')
ADMIN_ID = [int(id) for id in ADMIN_ID]



@admin_router.callback_query(F.data == 'manage_admins')
async def manage_access(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Управление админами', reply_markup=await get_manage_admins_kb())

@admin_router.callback_query(F.data == 'add_admin')
async def set_admin(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_ID:
        return
    await callback.message.answer('Введите ID пользователя')
    await state.set_state(AdminStates.set_admin)

@admin_router.message(AdminStates.set_admin)
async def set_admin_id(message: Message, state: FSMContext):
    user_id = message.text
    user = await get_user(int(user_id))
    if user is None:
        await message.answer('Пользователь не зарегистрирован в боте')
        return
    await message.answer(f'Пользователь {user.name} - {user.tg_id}\nтеперь администратор')
    await set_admin_status(int(user_id), True)
    await state.clear()


@admin_router.callback_query(F.data == 'get_admins')
async def get_admins(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_ID:
        return
    admins = await get_admins_orm()
    if admins:
        for admin in admins:
            await callback.message.answer(f'{admin.name}\n{admin.tg_id}', reply_markup=await delete_admin_kb(admin.tg_id))
    else:
        await callback.answer('Нет администраторов')


@admin_router.callback_query(F.data.startswith('delete_admin_'))
async def delete_admin(callback: CallbackQuery):
    tg_id = callback.data.split('_')[-1]
    await delete_admin_orm(int(tg_id))
    await callback.message.edit_text(f'Администратор {tg_id} удален')
    await asyncio.sleep(1)
    await callback.message.delete()



@admin_router.callback_query(F.data == 'manage_vip_users')
async def manage_vip_users(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Управление VIP пользователями', reply_markup=await get_manage_vip_users_kb())


@admin_router.callback_query(F.data == 'get_vip_users')
async def get_vips(callback: CallbackQuery):
    
    vips = await get_vip_users_orm()
    if vips:
        for vip in vips:
            await callback.message.answer(f'{vip.name}\n{vip.tg_id}', reply_markup=await delete_vip_kb(vip.tg_id))
    else:
        await callback.answer('Нет VIP пользователей')
        


@admin_router.callback_query(F.data.startswith('delete_vip_'))
async def delete_vip(callback: CallbackQuery):
    tg_id = callback.data.split('_')[-1]
    await delete_vip_orm(int(tg_id))
    await callback.message.edit_text(f'VIP пользователь {tg_id} убран')
    await asyncio.sleep(1)
    await callback.message.delete()


@admin_router.callback_query(F.data == 'add_vip')
async def add_vip(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите ID пользователя')
    await state.set_state(AdminStates.set_vip)


@admin_router.message(AdminStates.set_vip)
async def set_vip_id(message: Message, state: FSMContext):
    user_id = message.text
    user = await get_user(int(user_id))
    if user is None:
        await message.answer('Пользователь не зарегистрирован в боте')
        return
    if user.is_vip:
        await message.answer('Пользователь уже VIP')
        return
    await message.answer(f'Пользователь {user.name} - {user.tg_id}\nтеперь VIP')
    await set_vip_status(int(user_id), True)
    await state.clear()


@admin_router.callback_query(F.data.in_(['admin_panel', 'back_to_admin_menu']))
async def tovmas_kb(callback : CallbackQuery):
    

    if callback.from_user.id in ADMIN_ID:
        await callback.message.edit_text('Админ панель', reply_markup= await get_super_admin_kb())
    
    user = await get_user(int(callback.from_user.id))
    
    if user and user.is_admin:
        await callback.message.edit_text("Админ панель", reply_markup=await admin_kb())
            

