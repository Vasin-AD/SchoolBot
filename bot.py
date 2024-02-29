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


@bot.message_handler(commands=['pogoda'])
def pogoda(message):
    responce = requests.get(
        url='https://api.weather.yandex.ru/v2/informers',
        params={'lat' : 56.316659, 'lon' : 44.029055, 'lang' : 'ru_RU'},
        headers={'X-Yandex-API-Key' : 'c8ef6c5f-d118-406e-b409-1314691110db'}
    )

    data = responce.json()
    temp = data["fact"]["temp"]
    condition = data["fact"]["condition"]

    feels_like = data["fact"]["feels_like"]
    bot.send_message(message.chat.id, f"Температура: {temp}\nОщущаемая температура: {feels_like}\n{condition}")


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



bot.polling()