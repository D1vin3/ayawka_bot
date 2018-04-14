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
from utils import create_inline_keyboard, create_keyboard, formatItems
from telegramcalendar import create_calendar


current_shown_dates = {}
bot = TeleBot(token)
logger = telebot.logger
telebot.logger.setLevel(logging.ERROR)

db = DBHelper()
session = SessionDb()
db.setup()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Здравствуйте, я бот Аяшки из СДУ.")
    bot.send_message(
        message.chat.id, "Выберите интересующую вас услугу...",
        reply_markup=create_keyboard(main_buttons_without_img, 1)
    )
    # dbhelper.set_state(message.chat.id, config.States.S_CHOOSE_LOCATION.value)


@bot.message_handler(commands=['Нужно_передать_вещь_(через_кого_то)'])
def send_crypto(message):
    print('Клиент')
    bot.send_message(
        message.chat.id, "Загрузка...",
        reply_markup=create_keyboard(['/Главная'], 1)
    )
    bot.send_message(
        message.chat.id, "Пожалуйста, укажите интересующий вас маршрут",
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
    # bot.send_message(
    #     message.chat.id, "Выберите интересующую вас услугу...",
    #     reply_markup=create_keyboard(main_buttons_without_img, 1)
    # )
    dbhelper.set_state(message.chat.id, config.States.S_CHOOSE_LOCATION.value)


@bot.message_handler(commands=["Мои_заявки"])
def get_own_orders(message):
    print('МОИ ЗАЯВКИ')
    chat_id = message.chat.id
    orders = db.get_own_orders(chat_id)
    if len(orders) is not 0:
        for order in orders:
            text = "Откуда: {} \nКуда: {} \nНачальная дата: {} \nКонечная дата: {} \nТип перевозки: {}\n\n". \
                format(order[2], order[3], order[4], order[5], order[6])
            bot.send_message(chat_id, text, reply_markup=create_inline_keyboard(order, 'deleteOrder'))
    else:
        text = "Список ваших заявок пуст. Добавьте первое, нажав на /Нужно_передать_вещь_(через_кого_то)"
        bot.send_message(chat_id, text)

### - Uncomment this
# @bot.message_handler(commands=["Еду_в_другой_город,_могу_передать_вещь"])
# def get_own_orders(message):
#     print('Еду_в_другой_город,_могу_передать_вещь')
#     chat_id = message.chat.id
#     orders = db.get_orders()
#
#     if len(orders) is not 0:
#         for order in orders:
#             user = bot.get_chat(order[1])
#             username = str()
#             if hasattr(user, 'username'):
#                 username = "@{}".format(user.username)
#             else:
#                 username = "{} {}".format(user.first_name, user.last_name)
#             print('username is {}'.format(username))
#             text = "{} продает: {} \nСумма: {} \nЦена по курсу: {} \nГород: {} \nКомиссия в процентах: {}\n\n". \
#                 format(username, order[2], order[3], order[4], order[5], order[6])
#             bot.send_message(chat_id, text)
#     else:
#         text = "В данный момент записей нет. Станьте первым кто добавит, нажав на /Продать"
#         bot.send_message(chat_id, text)

    #####################################################################################################################
    """
     Handlers
    """


# # 2 - ENTER_SUM
# @bot.message_handler(func=lambda message: dbhelper.get_current_state(message.chat.id) == config.States.S_ENTER_SUM.value)
# def user_entering_crypto(message):
#     print('S_ENTER_SUM look')
#     chat_id = message.chat.id
#     print(message.text)
#     state = dbhelper.get_current_state(message.chat.id)
#     print('state is {}'.format(state))
#     bot.send_message(message.chat.id, "На какую сумму продаете($)?")
#     dbhelper.set_state(chat_id, config.States.S_CHOOSE_CURRENCY_SITE.value)


# 4 - CHHOSE CURRENCY
@bot.message_handler(
    func=lambda message: dbhelper.get_current_state(message.chat.id) == config.States.S_CHOOSE_CURRENCY_SITE.value)
def user_entering_currency(message):
    print('S_ENTER_CURRENCY_SITE is called')
    chat_id = message.chat.id
    price = message.text
    print(price)
    bot.send_message(
        message.chat.id, "По какому курсу продаете?",
        reply_markup=create_inline_keyboard(currency_site_buttons, type='last_date')
    )
    session.update_session(chat_id, price=price)
    print('--------------------------------------------------------------------')


# 5 - ENTER OWN CURRENCY SITE
@bot.message_handler(
    func=lambda message: dbhelper.get_current_state(message.chat.id) == config.States.S_TYPE_OWN_CURRENCY_SITE.value)
def user_entering_currency(message):
    print('S_TYPE_OWN_CURRENCY_SITE is called')
    chat_id = message.chat.id
    cur_site = message.text
    print(cur_site)
    bot.send_message(
        chat_id, 'В каком городе продаете?',
        reply_markup=create_keyboard(['/Сбросить', '/Главная'], 1)
    )
    session.update_session(chat_id, cur_site=cur_site)
    dbhelper.set_state(chat_id, config.States.S_ENTER_CITY.value)
    print('--------------------------------------------------------------------')



# 6 - ENTER CITY
@bot.message_handler(
    func=lambda message: dbhelper.get_current_state(message.chat.id) == config.States.S_ENTER_CITY.value)
def user_entering_city(message):
    print('S_ENTER_CITY is working')
    chat_id = message.chat.id
    city = message.text
    print(city)
    bot.send_message(
        chat_id, "Выберите размер комиссии (%)",
        reply_markup=create_inline_keyboard(marginality_amount_buttons, type='marginality')
    )
    session.update_session(chat_id, city=city)
    dbhelper.set_state(chat_id, config.States.S_CHOOSE_MARGINALITY.value)
    print('--------------------------------------------------------------------')


# # 5 - CHOOSE MARGINALITY
# @bot.message_handler(func=lambda message: dbhelper.get_current_state(message.chat.id) == config.States.S_CHOOSE_MARGINALITY.value)
# def user_entering_sum(message):
#     print('S_CHOOSE_MARGINALITY N is working')
#     city = message.text
#     print(city)
#     state = dbhelper.get_current_state(message.chat.id)
#     print('state is {}'.format(state))
#     bot.send_message(
#         message.chat.id, "Запись успешна добавлена",
#         reply_markup=create_keyboard(main_buttons_without_img, 1)
#     )
#     session.update_session(message.chat_id, city=city)
#     dbhelper.set_state(message.chat.id, config.States.S_START.value)


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    chat_id = call.message.chat.id
    data = call.data.split('.')
    print('------{}'.format(data))
    type = data[0]
    id = int(''.join(filter(lambda x: x.isdigit(), data[-1])))
    print('CALLBACK IS CALLED')
    print(id)
    now = datetime.datetime.now()               #Current date

    if type == 'source':
        source = ''.join(source_buttons[id - 1].split('.')[-1].strip())
        print('source is {}'.format(source))
        bot.send_message(
            chat_id, "Пожалуйста, укажите пункт назначения...",
            reply_markup=create_inline_keyboard(destination_buttons, type='destination')
        )
        session.create_session_with_source(chat_id, source=source)

    elif type == 'destination':
        date = (now.year, now.month)
        # current_shown_dates[chat_id] = date  # Saving the current date in a dict
        markup = create_calendar(now.year, now.month, isFirst=True)

        bot.send_message(chat_id, "Выберите начальную дату...", reply_markup=markup)
        destination = ''.join(destination_buttons[id - 1].split('.')[-1].strip())
        print('destination is {}'.format(destination))
        session.update_session(chat_id, destination=destination)

        # dbhelper.set_state(chat_id, config.States.S_CHOOSE_CURRENCY_SITE.value)

    elif type == 'first_date':
        date = (now.year, now.month)
        first_date = data[-1].strip()
        print('first_date is {}'.format(first_date))
        # current_shown_dates[chat_id] = date  # Saving the current date in a dict
        markup = create_calendar(now.year, now.month)
        bot.send_message(chat_id, "Выберите конечную дату...", reply_markup=markup)
        session.update_session(chat_id, first_date=first_date)

    elif type == 'last_date':
        # print('last_date is PRESSED')
        date = (now.year, now.month)
        last_date = data[-1].strip()
        print('last_date is {}'.format(last_date))

        bot.send_message(
            chat_id, "Выберите тип поездки...",
            reply_markup=create_inline_keyboard(travel_types_buttons, type='type')
        )
        session.update_session(chat_id, last_date=last_date)

    elif type == 'type':
        # print('type is pressed')
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

    elif type == 'deleteOrder':
        print('id is {}'.format(id))
        db.delete_order(id)
        orders = db.get_own_orders(chat_id)
        print('deleted')
        # print(orders)
        bot.send_message(
            chat_id, 'Объявление успешно удалено',
            reply_markup=create_keyboard(main_buttons_without_img, 1)
        )

        # bot.send_message(
        #     chat_id, "Выберите тип поездки...",
        #     reply_markup=create_inline_keyboard(travel_types_buttons, type='type')
        # )

        #     order = session.get_session(chat_id)
        #     print(order)
        #     crypto, price, cur_site, city, marginality = order['crypto'], order['price'], \
        #                                                  order['cur_site'], order['city'], order['marginality']
        #
        #     db.add_order(chat_id, crypto, price, cur_site, city, marginality)
        #     dbhelper.set_state(call.message.chat.id, config.States.S_START.value)

    print('--------------------------------------------------------------------')

    # elif type == 'currency':
    #     if id != 8:
    #         cur_list = currency_site_buttons[id - 1].split('.')[1:]
    #         cur_site = '{}.{}'.format(cur_list[0], cur_list[1])
    #         print('cur_site is {}'.format(cur_site))
    #         bot.send_message(
    #             chat_id, 'В каком городе продаете?',
    #             reply_markup=create_keyboard(['/Сбросить', '/Главная'], 1)
    #         )
    #         session.update_session(chat_id, cur_site=cur_site)
    #         dbhelper.set_state(chat_id, config.States.S_ENTER_CITY.value)
    #     else:
    #         print('other currency')
    #         bot.send_message(
    #             chat_id, "Пожалуйста, введите собственный вариант сайта с курсом криптовалют..."
    #         )
    #         dbhelper.set_state(chat_id, config.States.S_TYPE_OWN_CURRENCY_SITE.value)
    #     print('--------------------------------------------------------------------')
    #
    # elif type == 'marginality':
    #     # if data[-1].contains
    #     marginality = marginality_amount_buttons[id].split()[-1]
    #     print(marginality)
    #     bot.send_message(
    #         call.message.chat.id, "Запись успешна добавлена",
    #         reply_markup=create_keyboard(main_buttons_without_img, 1)
    #     )
    #     session.update_session(chat_id, marginality=marginality)
    #     order = session.get_session(chat_id)
    #     print(order)
    #     crypto, price, cur_site, city, marginality = order['crypto'], order['price'], \
    #                                                  order['cur_site'], order['city'], order['marginality']
    #
    #     db.add_order(chat_id, crypto, price, cur_site, city, marginality)
    #     dbhelper.set_state(call.message.chat.id, config.States.S_START.value)
    #     print('--------------------------------------------------------------------')
    #
    # elif type == 'deleteOrder':
    #     db.delete_order(id)
    #     db.get_own_orders(chat_id)
    #     print('deleted')
    #     bot.send_message(
    #         chat_id, 'Объявление успешно удалено',
    #         reply_markup=create_keyboard(main_buttons_without_img, 1)
    #     )
    #     print('--------------------------------------------------------------------')


# @bot.callback_query_handler(func=lambda call: call.data == 'next-month')
# def next_month(call):
#     chat_id = call.message.chat.id
#     saved_date = current_shown_dates.get(chat_id)
#     if saved_date is not None:
#         year, month = saved_date
#         month += 1
#         if month > 12:
#             month = 1
#             year += 1
#         date = (year,month)
#         current_shown_dates[chat_id] = date
#         markup = create_calendar(year, month)
#         bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
#         bot.answer_callback_query(call.id, text="")
#     else:
#         #Do something to inform of the error
#         pass
#
#
# @bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
# def previous_month(call):
#     chat_id = call.message.chat.id
#     saved_date = current_shown_dates.get(chat_id)
#     if saved_date is not None:
#         year, month = saved_date
#         month -= 1
#         if month < 1:
#             month = 12
#             year -= 1
#         date = (year, month)
#         current_shown_dates[chat_id] = date
#         markup = create_calendar(year, month)
#         bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
#         bot.answer_callback_query(call.id, text="")
#     else:
#         #Do something to inform of the error
#         pass


# # По команде /Сбросить будем сбрасывать состояния, возвращаясь к началу диалога
# @bot.message_handler(commands=["Сбросить"])
# def cmd_reset(message):
#     bot.send_message(
#         message.chat.id, "Все ваши действия были отменены. Пожалуйста, выберите из списка одну из услуг...",
#         reply_markup=create_inline_keyboard(from_to_locations_buttons, type='crypto')
#     )
    # dbhelper.set_state(message.chat.id, config.States.S_CHOOSE_LOCATION.value)


print('Bot has been switched on')
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as ex:
        logger.error(ex)
