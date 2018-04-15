import json
import sqlite3
import config
import datetime
from vedis import Vedis


def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except KeyError:
            # тут желательно как-то обработать ситуацию
            return False


def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            print('{} with {}'.format(user_id, db[user_id]))
            return db[user_id]
        except KeyError:
            return config.States.S_START.value  # значение по умолчанию - начало диалога


class SessionDb:

    def create_session_with_source(self, user_id, source):
        value = {
            'source': source,
            'destination': '',
            'first_date': '',
            'last_date': '',
            'type': '',
            'dr_source': '',
            'dr_destination': '',
        }

        value = json.dumps(value)
        with Vedis(config.session_file) as db:
            try:
                db[user_id] = value
                return True
            except KeyError:
                # тут желательно как-то обработать ситуацию
                return False

    def get_session(self, user_id):
        with Vedis(config.session_file) as db:
            try:
                # print('{} with {}'.format(user_id, db[user_id]))
                value = json.loads(db[user_id])
                return value
            except KeyError:
                return 'no session for this user'

    def update_session(self, user_id, source=None, destination=None, first_date=None, last_date=None, type=None,
                       dr_source=None, dr_destination=None):
        with Vedis(config.session_file) as db:
            try:
                print('{} with {}'.format(user_id, db[user_id]))
                value = db[user_id]
                value = json.loads(value)
                if source is not None:
                    value['source'] = source
                elif destination is not None:
                    value['destination'] = destination
                elif first_date is not None:
                    value['first_date'] = first_date
                elif last_date is not None:
                    value['last_date'] = last_date
                elif type is not None:
                    value['type'] = type
                elif dr_source is not None:
                    value['dr_source'] = dr_source
                elif dr_destination is not None:
                    value['dr_destination'] = dr_destination
                value = json.dumps(value)
                db[user_id] = value
                return db[user_id]
            except KeyError:
                return 'no session for this user'


class DBHelper:
    def __init__(self, dbname="data.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.setup()

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS orders (id integer primary key, " \
               "user text, " \
               "source text, " \
               "destination text, " \
               "first_date text, " \
               "last_date text," \
               "type text," \
               "created_datetime datetime)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_order(self, user, source, destination, first_date, last_date, type):
        now = datetime.datetime.now()
        stmt = "INSERT INTO orders (user, source, destination, first_date, last_date, type, " \
               "created_datetime) VALUES (?, ?, ?, ?, ?, ?, ?)"
        args = (user, source, destination, first_date, last_date, type, now)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_own_orders(self, username):
        stmt = "SELECT * FROM orders where user = (?)"
        args = (username,)
        items = []
        for row in self.conn.execute(stmt, args):
            items.append(row)
        print(items)
        return items

    def delete_order(self, id):
        stmt = "DELETE FROM orders WHERE id = (?)"
        args = (id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_all(self):
        stmt = "DELETE * FROM orders"
        self.conn.execute(stmt)
        self.conn.commit()

    def get_orders(self):
        stmt = "SELECT * FROM orders"
        items = []
        for row in self.conn.execute(stmt):
            items.append(row)
        print(items)
        return items

    def drop_table(self):
        stmt = "DROP TABLE orders"
        self.conn.execute(stmt)
        print('dropped')
        return 'done'

    def search_order(self, source, destination):
        items = list()
        stmt = "SELECT * FROM orders WHERE source = (?) AND destination = (?)"
        args = (source, destination)
        for row in self.conn.execute(stmt, args):
            items.append(row)
        return items
