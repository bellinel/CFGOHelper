from sqlalchemy import select
from database.engine import Users
from database.engine import Database

async def create_user(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            user = Users(tg_id=tg_id, balance=0, free_period=3)
            session.add(user)
            await session.commit()
            return user
    except Exception as e:
        print('Ошибка в функции create_user:', e)
        return None
    finally:
        await db.close()
    

async def get_user(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            user = await session.execute(select(Users).where(Users.tg_id == tg_id))
            return user.scalar_one_or_none()
    except Exception as e:
        print('Ошибка в функции get_user:', e)
        return None
    finally:
        await db.close()


async def decrement_free_period(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.tg_id == tg_id))
            user = result.scalar_one_or_none()
            if user and user.free_period > 0:
                user.free_period -= 1
                await session.commit()
                return user.free_period
            return None
    except Exception as e:
        print('Ошибка в функции decrement_free_period:', e)
        return None
    finally:
        await db.close()        

async def add_balance(tg_id: int, amount: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.tg_id == tg_id))
            user = result.scalar_one_or_none()
            if user:
                user.balance = user.balance + amount
                await session.commit()
                return user
            return None
    except Exception as e:
        print('Ошибка в функции add_balance:', e)
        return None
    finally:
        await db.close()

async def get_balance(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.tg_id == tg_id))
            user = result.scalar_one_or_none()
            return user.balance
    except Exception as e:
        print('Ошибка в функции get_balance:', e)
        return None
    finally:
        await db.close()


async def decrement_balance(tg_id: int, amount: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.tg_id == tg_id))
            user = result.scalar_one_or_none()
            if user and user.balance >= amount:
                user.balance -= amount
                await session.commit()
                return user
            return False
    except Exception as e:
        print('Ошибка в функции decrement_balance:', e)
        return None
    finally:
        await db.close()


async def get_free_period(tg_id: int):
    db = Database()
    try:
        async with db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.tg_id == tg_id))
            user = result.scalar_one_or_none()
            if user.is_admin:
                return 1
            return user.free_period
    except Exception as e:
        print('Ошибка в функции get_free_period:', e)
        return None
    finally:
        await db.close()