#!/usr/bin/python
# -*- coding: utf-8 -*-

import emoji
import config
import dbhelper
import logging
import telebot
import datetime
from telebot import TeleBot, types
from config import token
from dbhelper import DBHelper, SessionDb
from buttons import source_buttons, main_buttons_without_img, \
    currency_site_buttons, marginality_amount_buttons, travel_types_buttons, reset_buttons, destination_buttons
from utils import create_inline_keyboard, create_keyboard, formatItems, from_string_to_datetime, from_datetime_to_string
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
    orders = db.get_orders()
    bot.send_message(message.chat.id, "Здравствуйте, я бот Аяшки из СДУ.")
    bot.send_message(
        message.chat.id, "Выберите интересующую вас услугу...",
        reply_markup=create_keyboard(main_buttons_without_img, 1)
    )
    # dbhelper.set_state(message.chat.id, config.States.S_CHOOSE_LOCATION.value)


@bot.message_handler(commands=['Отправить_посылку'])
def send_crypto(message):
    print('Клиент')
    bot.send_message(
        message.chat.id, "...",
        reply_markup=create_keyboard(['/Главная'], 1)
    )
    bot.send_message(
        message.chat.id, "Откуда: ",
        reply_markup=create_inline_keyboard(source_buttons, type='source')
    )
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
            source, destination, first_date, last_date, travel_type, created_datetime = \
                order[2], order[3], order[4], order[5], order[6], order[7]

            created_datetime = from_string_to_datetime(created_datetime)
            created_datetime = from_datetime_to_string(created_datetime, rus_loc=True)
            text = "Откуда: {} \nКуда: {} \nНачальная дата: {} \nКонечная дата: {} \n" \
                   "Тип перевозки: {} \nДата создания объявления: {}\n\n". \
                format(source, destination, first_date, last_date, travel_type, created_datetime)
            bot.send_message(chat_id, text, reply_markup=create_inline_keyboard(order, 'deleteOrder'))
    else:
        text = "Список ваших объявлений пуст. Добавьте первое, нажав на /Отправить_посылку"
        bot.send_message(chat_id, text)


@bot.message_handler(commands=["Могу_доставить"])
def get_own_orders(message):
    print('Еду_в_другой_город,_могу_передать_вещь')
    chat_id = message.chat.id

    bot.send_message(
        chat_id, "Откуда: ",
        reply_markup=create_inline_keyboard(source_buttons, type='dr_source')
    )
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
        now = datetime.datetime.now()               #Current date
    except ValueError:
        pass

    if type == 'source':
        source = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('source is {}'.format(source))
        bot.send_message(
            chat_id, "Куда: ",
            reply_markup=create_inline_keyboard(destination_buttons, type='destination')
        )
        session.create_session_with_source(chat_id, source=source)

    elif type == 'destination':
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict
        markup = create_calendar(now.year, now.month, isFirst=True)

        bot.send_message(chat_id, "Выберите начальную дату...", reply_markup=markup)
        destination = ''.join(destination_buttons[id - 1].split('.')[-1].strip())
        print('destination is {}'.format(destination))
        session.update_session(chat_id, destination=destination)

        # dbhelper.set_state(chat_id, config.States.S_CHOOSE_CURRENCY_SITE.value)

    elif type == 'first_date':
        #############################################################################################
        if data[1] == 'next-month':
            markup, date = next_month_markup(current_shown_dates, call, isFirst=True)
            current_shown_dates[chat_id] = date
            bot.edit_message_text("Пожалуйста, выберите начальную дату...", call.from_user.id,
                                  call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            return

        elif data[1] == 'previous-month':
            markup, date = previous_month_markup(current_shown_dates, call, isFirst=True)
            current_shown_dates[chat_id] = date
            bot.edit_message_text("Пожалуйста, выберите начальную дату...", call.from_user.id,
                                  call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
            return
        #############################################################################################
        else:
            date = (now.year, now.month)
            first_date = data[-1].strip()
            print('first_date is {}'.format(first_date))
            current_shown_dates[chat_id] = date  # Saving the current date in a dict
            markup = create_calendar(now.year, now.month)
            bot.send_message(chat_id, "Выберите конечную дату...", reply_markup=markup)
            session.update_session(chat_id, first_date=first_date)

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
        print(order)
        source, destination, first_date, last_date, type = \
            order['source'], order['destination'], order['first_date'], \
            order['last_date'], order['type']

        db.add_order(chat_id, source, destination, first_date, last_date, type)
        bot.send_message(
            chat_id, "Запись успешна добавлена",
            reply_markup=create_keyboard(main_buttons_without_img, 1)
        )

    elif type == 'dr_source':
        dr_source = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('dr_source is {}'.format(dr_source))
        bot.send_message(
            chat_id, "Куда: ",
            reply_markup=create_inline_keyboard(destination_buttons, type='dr_destination')
        )
        session.update_session(chat_id, dr_source=dr_source)

    elif type == 'dr_destination':
        dr_destination = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('dr_destination is {}'.format(dr_destination))
        order = session.get_session(chat_id)
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

                source, destination, first_date, last_date, travel_type, created_datetime = \
                    order[2], order[3], order[4], order[5], order[6], order[7]

                created_datetime = from_string_to_datetime(created_datetime)
                created_datetime = from_datetime_to_string(created_datetime, rus_loc=True)

                text = "Автор: {} \nОткуда: {} \nКуда: {} \nНачальная дата: {} \n" \
                       "Конечная дата: {} \nТип перевозки: {}\nДата создания объявления: {}\n\n". \
                    format(username, source, destination, first_date, last_date,
                           travel_type, created_datetime)
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
