# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : util_sqlite.py
@create time: 2024/2/22 2:51 PM
@modify time: 2024/2/22 2:51 PM
@describe   : 
-------------------------------------------------
"""
import sqlite3

from utils.util_print import print2


class SQLiteDB:
    def __init__(self, db_file='lianjia.db'):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def check_cursor(self):
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        return self.cursor

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def execute(self, sql, params=()):
        self.check_cursor()
        self.cursor.execute(sql, params)
        self.conn.commit()

    def query(self, sql):
        self.check_cursor()
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        columns = [column[0] for column in self.cursor.description]

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return result

    def commit(self):
        self.conn.commit()

    def insert(self, table, data, echo=False):
        fields = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        sql = f'INSERT INTO {table} ({fields}) VALUES ({placeholders})'
        data_values = tuple(data.values())
        if echo:
            formatted_sql = sql
            for value in data_values:
                formatted_sql = formatted_sql.replace('?', f"'{value}'", 1)
            print2(formatted_sql)
        self.execute(sql, data_values)

    def batch_insert(self, table, data):
        if len(data) == 0:
            raise Exception("Data is null")
        keys = data[0].keys()
        placeholders = ','.join(':' + key for key in keys)
        insert_statement = f'INSERT INTO {table} ({",".join(keys)}) VALUES ({placeholders})'
        self.check_cursor()
        for item in data:
            self.cursor.execute(insert_statement, item)
        self.conn.commit()

    def upsert(self, table, data):
        placeholders = ", ".join(["?"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(sql, values)

    def update(self, table, data, condition):
        set_fields = ', '.join([f'{k}=?' for k in data.keys()])
        sql = f'UPDATE {table} SET {set_fields} WHERE {condition}'
        self.execute(sql, tuple(data.values()))

    def delete(self, table, condition):
        self.check_cursor()
        sql = f'DELETE FROM {table} WHERE {condition}'
        self.execute(sql)

    def count(self, table):
        self.check_cursor()
        self.cursor.execute(f"SELECT count(*) FROM {table};")
        return self.cursor.fetchall()[0][0]

    def select(self, table, condition=''):
        sql = f'SELECT * FROM {table}'
        if condition:
            sql += f' WHERE {condition} ;'
        return self.query(sql)


db = SQLiteDB()
