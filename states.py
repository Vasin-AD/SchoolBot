from telebot.handler_backends import State, StatesGroup


class ScheduleStates(StatesGroup):
    waiting_class = State()
    waiting_mark = State()
    waiting_day = State()
    