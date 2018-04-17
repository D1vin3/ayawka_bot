# -*- coding: utf-8 -*-
from telebot import types
import calendar


def create_calendar(year, month, isFirst=False):
    if isFirst:
        type = 'first_date'
    else:
        type = 'last_date'
    markup = types.InlineKeyboardMarkup()
    # First row - Month and Year
    row = list()
    row.append(types.InlineKeyboardButton(calendar.month_name[month]+" "+str(year), callback_data="ignore"))
    markup.row(*row)
    # Second row - Week Days
    week_days = ["Пон", "Вт", "Ср", "Чт", "Пн", "Суб", "Вос"]
    row = list()
    for day in week_days:
        row.append(types.InlineKeyboardButton(day, callback_data="ignore"))
    markup.row(*row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                mm = '{0:02d}'.format(month)
                row.append(types.InlineKeyboardButton(str(day), callback_data='{}.{}-{}-{}'.format(type, day, mm, year)))
        markup.row(*row)
    # Last row - Buttons
    row = list()
    row.append(types.InlineKeyboardButton("<", callback_data="{}.previous-month.999".format(type)))
    row.append(types.InlineKeyboardButton(" ", callback_data="ignore.999"))
    row.append(types.InlineKeyboardButton(">", callback_data="{}.next-month.999".format(type)))
    markup.row(*row)
    return markup


def next_month_markup(current_shown_dates, call, isFirst=False):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if saved_date is not None:
        year, month = saved_date
        month += 1
        if month > 12:
            month = 1
            year += 1
        date = (year, month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year, month, isFirst=isFirst)
        return markup, date


def previous_month_markup(current_shown_dates, call, isFirst=False):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if saved_date is not None:
        year, month = saved_date
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        date = (year, month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year, month, isFirst=isFirst)
        return markup, date
