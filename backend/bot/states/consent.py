from aiogram.fsm.state import State, StatesGroup

class ConsentState(StatesGroup):
    awaiting_consent = State()