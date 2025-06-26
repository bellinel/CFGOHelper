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
        print(e)
        return None
    finally:
        await db.close()
    

async def get_admins_orm():
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(
                select(Users).where(Users.is_admin == True)
            )
            return result.scalars().all()
    except Exception as e:
        print(f'Ошибка при получении администраторов: {e}')
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
        print(e)
        return None