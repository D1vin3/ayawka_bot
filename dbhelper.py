import json
import sqlite3
import config
from vedis import Vedis


def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
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

    def create_session_with_location(self, user_id, location):
        value = {
            'location': location,
            'first_date': '',
            'last_date': '',
            'type': '',
        }

        value = json.dumps(value)
        with Vedis(config.session_file) as db:
            try:
                db[user_id] = value
                return True
            except:
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


    def update_session(self, user_id, location=None, first_date=None, last_date=None, type=None):
        with Vedis(config.session_file) as db:
            try:
                print('{} with {}'.format(user_id, db[user_id]))
                value = db[user_id]
                value = json.loads(value)
                if location is not None:
                    value['location'] = location
                elif first_date is not None:
                    value['first_date'] = first_date
                elif last_date is not None:
                    value['last_date'] = last_date
                elif type is not None:
                    value['type'] = type
                # elif weight is not None:
                #     value['weight'] = weight
                # elif price is not None:
                #     value['price'] = price
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
                   "location text, " \
                   "first_date text, " \
                   "last_date text," \
                   "type text)"
                   # "weight text," \
                   # "price text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_order(self, user, location, first_date, last_date, type):
        stmt = "INSERT INTO orders (user, location, first_date, last_date, type) VALUES " \
               "(?, ?, ?, ?, ?)"
        args = (user, location, first_date, last_date, type)
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
        args = (id, )
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
