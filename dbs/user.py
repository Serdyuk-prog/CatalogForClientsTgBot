import json
import sqlite3
from io import StringIO
import os.path
from dbs.guser import GUser
from typing import Optional


class User:
    def __init__(self, user_id):
        self.db_name = 'dbs/gnrl.db'
        self.id = user_id
        self.dumped = self.__try_get_user()
        if self.dumped is None:
            self.dumped = GUser([self.id, 2, None, None, None, None])

    def get_settings(self) -> dict:
        return {'on_page': self.dumped.on_page}

    def set_settings(self, on_page: int) -> dict:
        if on_page not in (1, 2):
            on_page = 2
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()

            try:
                # try to set settings
                con.execute('''UPDATE user SET on_page = ? WHERE id = ?''', (on_page, self.id,))
                con.commit()
                return {'on_page': on_page}

            except Exception as e:
                print('set_settings: ' + str(e))
                return {}

    def get_search(self) -> dict:
        return {
            'query': self.dumped.query,
            'way': self.dumped.way,
            'row': self.dumped.row,
            'sort': self.dumped.sort
        }

    def set_search(self, actual_search: dict) -> dict:
        if 'query' in actual_search.keys():
            if actual_search['query'] is not None and type(actual_search['query']) is not str:
                self.dumped.query = None
            elif actual_search['query'] != self.dumped.query:
                self.dumped.query = actual_search['query']
        if 'way' in actual_search.keys():
            if actual_search['way'] is not None and type(actual_search['way']) is not str:
                self.dumped.way = None
            elif actual_search['way'] != self.dumped.way:
                self.dumped.way = actual_search['way']
        if 'row' in actual_search.keys():
            if actual_search['row'] is not None and type(actual_search['row']) is not int:
                self.dumped.row = None
            elif actual_search['row'] != self.dumped.row:
                self.dumped.row = actual_search['row']
        if 'sort' in actual_search.keys():
            if actual_search['sort'] is not None and type(actual_search['sort']) is not int:
                self.dumped.sort = None
            elif actual_search['sort'] != self.dumped.sort:
                self.dumped.sort = actual_search['sort']

        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()

            try:
                # try to set settings
                con.execute('''UPDATE user SET 
                               query = ?, 
                               way = ?,
                               row = ?,
                               sort = ?
                               WHERE id = ?''', (self.dumped.query,
                                                 self.dumped.way,
                                                 self.dumped.row,
                                                 self.dumped.sort,
                                                 self.id))
                con.commit()
                return {
                    'query': self.dumped.query,
                    'way': self.dumped.way,
                    'row': self.dumped.row,
                    'sort': self.dumped.sort
                }

            except Exception as e:
                print('set_search: ' + str(e))
                return {}

    def reset_search(self):
        self.set_search({'query': '', 'way': '', 'row': 0})

    def __try_get_user(self) -> Optional[GUser]:
        with sqlite3.connect(self.db_name) as con:
            cur = con.cursor()

            try:
                # try to select user
                user_data = con.execute('''SELECT * FROM user WHERE id = ?''', (self.id,)).fetchone()
                if user_data is None:
                    # User is not created, create it!
                    con.execute('''INSERT INTO user (id) VALUES (?)''', (self.id,))
                    con.commit()
                    user_data = [self.id, 2, None, None, None, None]
                return GUser(user_data)

            except Exception as e:
                print('__try_get_user: ' + str(e))
                return None
