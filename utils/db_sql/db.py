import logging
import os
import sqlite3
import time


class Database:
    def __init__(self, path_to_db='main.db'):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False,
                fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()

        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()

        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id integer PRIMARY KEY,
            telegram_id integer NOT NULL,
            name varchar(255) NOT NULL
        );"""
        self.execute(sql, commit=True)

    def add_user(self, id, name):
        sql = "INSERT INTO Users (telegram_id, name) VALUES (?,?);"
        parameters = (id, name)
        self.execute(sql, parameters=parameters, commit=True)

    def check_user(self, user_id: int):
        sql = f"SELECT id FROM Users WHERE telegram_id={user_id}"
        return self.execute(sql, fetchone=True)

    def create_table_history(self):
        sql = """
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER NOT NULL,
            command varchar(255) NOT NULL,
            datetime varchar(255) NOT NULL,
            result varchar(255) NOT NULL
        );"""
        self.execute(sql, commit=True)

    def add_history(self, tg_id, command, datetime, result):
        sql = "INSERT INTO History (telegram_id, command, datetime, result) " \
              "VALUES (?,?,?,?);"
        parameters = (tg_id, command, datetime, result)
        self.execute(sql, parameters=parameters, commit=True)

    def get_history(self, tg_id):
        sql = f"SELECT * FROM History WHERE telegram_id={tg_id}"
        return self.execute(sql, fetchall=True)


def logger(statement):
    logging.info(statement)
