from sqlalchemy import update, select
from database.engine import Database
from database.engine import Users

async def set_admin_status(tg_id: int, status: bool):
    db = Database()
    try:
        async with db.session_factory() as session:
            await session.execute(update(Users).where(Users.tg_id == tg_id).values(is_admin=status))
            await session.commit()
    except Exception as e:
        print('Ошибка в функции set_admin_status:', e)
        return None
    finally:
        await db.close()
    

async def get_admins_orm():
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(
                select(Users).where(Users.is_admin == True).order_by(Users.tg_id)
            )
            return result.scalars().all()
    except Exception as e:
        print('Ошибка в функции get_admins_orm:', e)
        return None
    finally:
        await db.close()


async def delete_admin_orm(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            await session.execute(update(Users).where(Users.tg_id == tg_id).values(is_admin=False))
            await session.commit()
    except Exception as e:
        print('Ошибка в функции delete_admin_orm:', e)
        return None
    

async def get_vip_users_orm():
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.is_vip == True).order_by(Users.tg_id))
            return result.scalars().all()
    except Exception as e:
        print('Ошибка в функции get_vip_users_orm:', e)
        return None
    finally:
        await db.close()


async def delete_vip_orm(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            await session.execute(update(Users).where(Users.tg_id == tg_id).values(is_vip=False))
            await session.commit()
    except Exception as e:
        print('Ошибка в функции delete_vip_orm:', e)
        return None
    
async def set_vip_status(tg_id: int, status: bool):
    db = Database()
    try:
        async with db.session_factory() as session:
            user = await session.execute(select(Users).where(Users.tg_id == tg_id))
            if user.is_vip == status:
                return None
            else:
                await session.execute(update(Users).where(Users.tg_id == tg_id).values(is_vip=status))
                await session.commit()
    except Exception as e:
        print('Ошибка в функции set_vip_status:', e)
        return None
    finally:
        await db.close()