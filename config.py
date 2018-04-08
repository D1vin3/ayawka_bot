# -*- coding: utf-8 -*-
from enum import Enum
import emoji


token = '596910692:AAGJ-MKjRqScqZbSUjMC1sZCqrGhLQchfX0'
url = 'https://api.telegram.org/bot{0}/'.format(token)

db_file = "database.vdb"
session_file = "session.vdb"


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"                   # Начало нового диалога
    S_CHOOSE_CRYPTO = "1"           # location
    S_TYPE_OWN_CRYPTO = "2"         # location
    S_ENTER_SUM = "3"               # first_date
    S_CHOOSE_CURRENCY_SITE = "4"    # last_date
    S_TYPE_OWN_CURRENCY_SITE = "5"  # type
    S_ENTER_CITY = "6"              # weight
    S_CHOOSE_MARGINALITY = "7"      # price
