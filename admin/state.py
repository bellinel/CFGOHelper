from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    set_admin = State()
    set_vip = State()