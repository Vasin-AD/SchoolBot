import os
import telebot
import requests
import pandas as pd
from telebot import types

from states import ScheduleStates

from telebot.storage import StateMemoryStorage
from telebot import custom_filters # import some filters
from telebot import TeleBot

state_storage = StateMemoryStorage()

day_to_number = {
    "Понедельник" : 0, 
    "Вторник" : 1, 
    "Среда" : 2,
    "Четверг" : 3,
    "Пятница" : 4,
    "Суббота" : 5, 
    "Воскресенье" : 6
}


token = os.environ['TG_TOKEN']
bot = TeleBot(token, state_storage=state_storage)

bot.add_custom_filter(custom_filters.StateFilter(bot)) # state filter
bot.add_custom_filter(custom_filters.IsDigitFilter()) # this filter 
# cheks whether message.text is digit or not

@bot.message_handler(commands=['start'])
def start(message):

    name = message.from_user.first_name
    if message.from_user.last_name:
        name += message.from_user.last_name

    bot.send_message(message.chat.id, f"Привет {name}!")

@bot.message_handler(commands=['help'])
def start(message):

    bot.send_message(message.chat.id, f"Привет. Я тебе помогу разобраться в Телеграмм-Боте. \n /start -команда, служит только для запуска бота \n /help – команда выводит информацию о командах бота \n /schedule – команда , служит для получения расписания \n Надеюсь, ты разобрался в Телеграмм-Боте. Удачи!")

@bot.message_handler(commands=['schedule'])
def schedule(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(1, 12):
        btn = types.KeyboardButton(f"{i} Класс")
        markup.add(btn)

    bot.set_state(message.from_user.id, ScheduleStates.waiting_class, message.chat.id)
    bot.send_message(message.chat.id, "Выбери свой класс:", reply_markup=markup)
    

@bot.message_handler(state=ScheduleStates.waiting_class)
def get_class(message):
    number_class = int(message.text.split()[0])

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['number_class'] = number_class

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in ['А', 'Б', 'В', 'Г', 'Т', 'Т(ФИЗ)', 'Т(ИНФ)', 'Е', 'Э', 'Г', 'Г(ИСТ)', 'Г(АНГ)']:
        btn = types.KeyboardButton(i)
        markup.add(btn)

    bot.send_message(message.chat.id, "Выбери букву класса: ", reply_markup=markup)
    bot.set_state(message.from_user.id, ScheduleStates.waiting_mark, message.chat.id)


@bot.message_handler(state=ScheduleStates.waiting_mark)
def get_mark(message):
    mark = message.text

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['mark'] = mark
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in ['Понедельник','Вторник','Среда', 'Четверг','Пятница']:
        btn = types.KeyboardButton(i)
        markup.add(btn)
    
    bot.send_message(message.chat.id, "Выбери день", reply_markup=markup)
    bot.set_state(message.from_user.id, ScheduleStates.waiting_day, message.chat.id)


@bot.message_handler(state=ScheduleStates.waiting_day)
def get_day(message):
    day = message.text

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        
        _mark = data['mark']
        _class = data['number_class']

    try:
        excel_data = pd.read_excel(f'./data/{_class} Класс.xlsx', sheet_name=f"{_mark}", header=None).dropna()
        ans = [lesson for lesson in excel_data[day_to_number[day]]]
        ans = '\n'.join(ans)
        bot.send_message(message.chat.id, ans, reply_markup=types.ReplyKeyboardRemove())
        bot.delete_state(message.from_user.id, message.chat.id)
    except ValueError:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in ['А', 'Б', 'В', 'Г', 'Т', 'Т(ФИЗ)', 'Т(ИНФ)', 'Е', 'Э', 'Г', 'Г(ИСТ)', 'Г(АНГ)']:
            btn = types.KeyboardButton(i)
            markup.add(btn)
        bot.send_message(message.chat.id, "Такой буквы нет, выбери другую букву: ", reply_markup=markup)
        bot.set_state(message.from_user.id, ScheduleStates.waiting_mark, message.chat.id)
        
            

bot.polling()