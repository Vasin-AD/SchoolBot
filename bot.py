import os
import telebot
import requests

token = os.environ['TG_TOKEN']
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):

    name = message.from_user.first_name
    if message.from_user.last_name:
        name += message.from_user.last_name

    bot.send_message(message.chat.id, f"Привет {name}!")


@bot.message_handler(commands=['pogoda'])
def pogoda(message):
    qeqweq = "qeqq"
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

bot.polling()