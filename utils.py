# -*- coding: utf-8 -*-
import locale
from datetime import datetime
from math import ceil

from telebot import types


def from_string_to_datetime(string_date, fm="%Y-%m-%d %H:%M:%S.%f"):
    return datetime.strptime(string_date, fm)


def from_datetime_to_string(datetime_date, fm="%d %B/ %H:%M", rus_loc=False):
    if rus_loc:
        loc = locale.getlocale()
        locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))
        datetime = datetime_date.strftime(fm)
        locale.setlocale(locale.LC_ALL, loc)
        return datetime
    return datetime_date.strftime(fm)


def getItems(text):
    t = text.split(" ")
    return t[0], t[1], t[2], t[3]


def formatItems(isOwn, array):
    text = ""
    if not array:
        return 'К сожалению пока нет записей.'
    else:
        for elem in array:
            text += "{} продает: {} \nКоличество: {} \nЦена в долларах: {}\nКомиссия в процентах: {} \n\n".format(elem[1], elem[2], elem[3], elem[4], elem[5])
    return text


def create_keyboard(words=None, width=None):
        keyboard = types.ReplyKeyboardMarkup(row_width=width, resize_keyboard=True)
        for word in words:
            keyboard.add(types.KeyboardButton(text=word))
        return keyboard


def create_inline_keyboard(orders, type=None):
        keyboard = types.InlineKeyboardMarkup()
        callback_data = 'empty'

        if type == 'deleteOrder':
            return create_inline_button_for_delete(orders)
        elif type == 'showOrder':
            return create_inline_button_for_show()

        elif type == 'source_cities' or type == 'destination_cities' \
                or type == 'dr_source' or type == 'dr_destination':
            count = len(orders)
            max_i = ceil(count / 2)
            is_even = count % 2 == 0
            print(orders)
            for i, v in enumerate(range(0, count, 2)):
                # print(orders[v])
                if not is_even:
                    if i < max_i - 1:
                        print('normal iter')
                        first = orders[v]
                        second = orders[v+1]
                        print(first, second)
                    else:
                        print('max')
                        first = orders[v]
                        second = None
                        print(first, second)
                else:
                    first = orders[v]
                    second = orders[v+1]
                    print(first, second)

                btn_callback_data = '{}.{}'.format(type, str(int(first.split('.')[0])))
                btn = types.InlineKeyboardButton(text=first, callback_data=btn_callback_data)

                if second is not None:
                    btn_2_callback_data = '{}.{}'.format(type, str(int(second.split('.')[0])))
                    btn_2 = types.InlineKeyboardButton(text=second, callback_data=btn_2_callback_data)
                    keyboard.add(btn, btn_2)
                else:
                    keyboard.add(btn)
            return keyboard

        for i in range(len(orders)):
            item_id = str(int(orders[i].split('.')[0]))
            callback_data = '{}.{}'.format(type, item_id)

            btn = types.InlineKeyboardButton(text=orders[i], callback_data=callback_data)
            keyboard.add(btn)
        return keyboard


def create_inline_button_for_delete(order):
    keyboard = types.InlineKeyboardMarkup()
    callback_data = 'deleteOrder.{}'.format(order[0])
    btn = types.InlineKeyboardButton(text='Удалить объявление', callback_data=callback_data)
    keyboard.add(btn)
    return keyboard


def create_inline_button_for_show():
    keyboard = types.InlineKeyboardMarkup()
    return keyboard


def create_inline_keyboard_for_html(orders):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(len(orders)):
        btn = types.InlineKeyboardButton(text=orders[i], callback_data=orders[i])
        keyboard.add(btn)
    return keyboard
