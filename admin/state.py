from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    set_admin = State()
    