#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytz
import config
import dbhelper
import logging
import telebot
import datetime
import time
from telebot import TeleBot, types
from config import token
from dbhelper import DBHelper, SessionDb
from buttons import source_buttons, main_buttons_without_img, travel_types_buttons, \
    destination_buttons
from utils import create_inline_keyboard, create_keyboard, from_string_to_datetime, \
    from_datetime_to_string
from telegramcalendar import create_calendar, next_month_markup, previous_month_markup

current_shown_dates = {}
bot = TeleBot(token)
logger = telebot.logger
telebot.logger.setLevel(logging.ERROR)

db = DBHelper()
session = SessionDb()
db.setup()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    db.get_orders()
    bot.send_message(message.chat.id, "Здравствуйте! Этот бот найдет вам попутчика "
                                      "для передачи посылки в другой город")
    bot.send_message(
        message.chat.id, "Выберите интересующую вас услугу...",
        reply_markup=create_keyboard(main_buttons_without_img, 2)
    )


@bot.message_handler(commands=['Отправить_посылку'])
def send_crypto(message):
    bot.send_message(
        message.chat.id, "Откуда",
        reply_markup=create_keyboard(['/Главная'], 1))
    time.sleep(1.5)
    bot.send_message(
        message.chat.id, "Выберите город: ",
        reply_markup=create_inline_keyboard(source_buttons, type='source_cities'))
    dbhelper.get_current_state(message.chat.id)


@bot.message_handler(commands=["Главная"])
def cmd_reset(message):
    print('Главнавя')
    bot.send_message(
        message.chat.id, "Ваши действия были отменены. Пожалуйста, "
                         "выберите интересующую вас услугу...",
        reply_markup=create_keyboard(main_buttons_without_img, 1)
    )
    dbhelper.set_state(message.chat.id, config.States.S_CHOOSE_LOCATION.value)


@bot.message_handler(commands=["Мои_объявления"])
def get_own_orders(message):
    chat_id = message.chat.id
    orders = db.get_own_orders(chat_id)
    if len(orders) is not 0:
        for order in orders:
            source, destination, last_date, travel_type, created_datetime = \
                order[2], order[3], order[4], order[5], order[6]

            created_datetime = from_string_to_datetime(created_datetime)
            created_datetime += datetime.timedelta(hours=6)
            created_datetime = from_datetime_to_string(created_datetime, rus_loc=True)
            text = "Откуда: {} \nКуда: {} \nДата прибытия посылки: {} \n" \
                   "Тип перевозки: {} \nДата создания объявления: {}\n\n". \
                format(source, destination, last_date, travel_type, created_datetime)
            bot.send_message(chat_id, text, reply_markup=create_inline_keyboard(order, 'deleteOrder'))
    else:
        text = "Список ваших объявлений пуст. Добавьте первое, нажав на /Отправить_посылку"
        bot.send_message(chat_id, text)


@bot.message_handler(commands=["Могу_доставить"])
def get_own_orders(message):
    print('Еду_в_другой_город,_могу_передать_вещь')
    chat_id = message.chat.id
    bot.send_message(chat_id, "Откуда: ")
    time.sleep(1.5)
    bot.send_message(
        chat_id, "Выберите город: ",
        reply_markup=create_inline_keyboard(source_buttons, type='dr_source'))
    #####################################################################################################################


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    try:
        chat_id = call.message.chat.id
        data = call.data.split('.')
        print('------{}'.format(data))
        type = data[0]
        id = int(''.join(filter(lambda x: x.isdigit(), data[-1])))
        print('CALLBACK IS CALLED')
        now = datetime.datetime.now(tz=pytz.timezone('Asia/Almaty'))    # Current date
        print(now)
    except ValueError:
        pass

    if type == 'source_cities':
        source = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('source is {}'.format(source))
        bot.send_message(chat_id, "Куда: ")
        time.sleep(1.5)
        bot.send_message(
            chat_id, "Выберите город: ",
            reply_markup=create_inline_keyboard(destination_buttons, type='destination_cities'))
        session.create_session_with_source(chat_id, source=source)

    elif type == 'destination_cities':
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date             # Saving the current date in a dict
        markup = create_calendar(now.year, now.month)

        bot.send_message(chat_id, "Выберите желаемую дату прибытия посылки...", reply_markup=markup)
        destination = ''.join(destination_buttons[id - 1].split('.')[-1].strip())
        print('destination is {}'.format(destination))
        session.update_session(chat_id, destination=destination)

    elif type == 'last_date':
        #############################################################################################
        if data[1] == 'next-month':
            markup, date = next_month_markup(current_shown_dates, call)
            current_shown_dates[chat_id] = date
            bot.edit_message_text("Пожалуйста, выберите конечную дату...", call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            return

        elif data[1] == 'previous-month':
            markup, date = previous_month_markup(current_shown_dates, call)
            current_shown_dates[chat_id] = date
            bot.edit_message_text("Пожалуйста, выберите конечную дату...", call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            return
            #############################################################################################
        else:
            date = (now.year, now.month)
            last_date = data[-1].strip()
            print('last_date is {}'.format(last_date))

            bot.send_message(
                chat_id, "Выберите тип поездки...",
                reply_markup=create_inline_keyboard(travel_types_buttons, type='type')
            )
            session.update_session(chat_id, last_date=last_date)

    elif type == 'type':
        travel_type = ''.join(travel_types_buttons[id - 1].split('.')[-1].strip())
        print('type is {}'.format(travel_type))
        session.update_session(chat_id, type=travel_type)
        order = session.get_session(chat_id)
        source, destination, last_date, type = \
            order['source'], order['destination'], order['last_date'], order['type']

        db.add_order(chat_id, source, destination, last_date, type)
        bot.send_message(
            chat_id, "Запись успешна добавлена",
            reply_markup=create_keyboard(main_buttons_without_img, 1)
        )

    elif type == 'dr_source':
        dr_source = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('dr_source is {}'.format(dr_source))
        bot.send_message(chat_id, "Куда: ")
        time.sleep(1.5)
        bot.send_message(
            chat_id, "Выберите город: ",
            reply_markup=create_inline_keyboard(destination_buttons, type='dr_destination'))
        session.update_session(chat_id, dr_source=dr_source)

    elif type == 'dr_destination':
        dr_destination = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('dr_destination is {}'.format(dr_destination))
        order = session.get_session(chat_id)
        print('order from session is {}'.format(order))
        dr_source = order['dr_source']
        orders = db.search_order(source=dr_source, destination=dr_destination)

        if len(orders) is not 0:
            for order in orders:
                user = bot.get_chat(order[1])
                username = str()
                if hasattr(user, 'username'):
                    username = "@{}".format(user.username)
                else:
                    username = "{} {}".format(user.first_name, user.last_name)

                source, destination, last_date, travel_type, created_datetime = \
                    order[2], order[3], order[4], order[5], order[6]

                created_datetime = from_string_to_datetime(created_datetime)
                created_datetime += datetime.timedelta(hours=6)
                created_datetime = from_datetime_to_string(created_datetime, rus_loc=True)

                text = "Автор: {} \nОткуда: {} \nКуда: {} \nДата прибытия посылки: {} " \
                       "\nТип перевозки: {}\nДата создания объявления: {}\n\n". \
                    format(username, source, destination, last_date, travel_type, created_datetime)
                bot.send_message(chat_id, text, reply_markup=create_inline_keyboard(order, 'showOrder'))
        else:
            text = "Список объявлений пуст. Добавьте первое, нажав на /Отправить_посылку"
            bot.send_message(chat_id, text)

    elif type == 'deleteOrder':
        print('id is {}'.format(id))
        db.delete_order(id)
        print('deleted')
        bot.send_message(
            chat_id, 'Объявление успешно удалено',
            reply_markup=create_keyboard(main_buttons_without_img, 1)
        )


print('Bot has been switched on')
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as ex:
        logger.error(ex)
