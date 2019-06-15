import os

import psycopg2
from psycopg2 import sql


class DB:

    def __init__(self, psycopg_cursor_factory) -> None:
        self.psycopg_cursor_factory = psycopg_cursor_factory
        self.connection = None
        self.cursor = None

    def dynamic_get_row(self, table, column, value):
        try:
            self.connection = psycopg2.connect(os.environ["DATABASE_URL"])

            print("Database connection is established...")

            self.cursor = self.connection.cursor(cursor_factory=self.psycopg_cursor_factory)
            self.cursor.execute(
                sql.SQL("SELECT * FROM {} WHERE {} = %s LIMIT 1").format(sql.Identifier(table), sql.Identifier(column)),
                [value])

            return self.cursor.fetchone()
        except (Exception, psycopg2.Error) as error:
            print("Database connection error", error)
        finally:
            if self.connection is not None:
                self.cursor.close()
                self.connection.close()

                print("Database connection is closed...")

    def get_rows(self, query, variables):
        try:
            self.connection = psycopg2.connect(os.environ["DATABASE_URL"])

            print("Database connection is established...")

            self.cursor = self.connection.cursor(cursor_factory=self.psycopg_cursor_factory)
            self.cursor.execute(query, variables)

            return self.cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            print("Database connection error", error)
        finally:
            if self.connection is not None:
                self.cursor.close()
                self.connection.close()

                print("Database connection is closed...")

    def insert_rows(self, query, variables):
        try:
            self.connection = psycopg2.connect(os.environ["DATABASE_URL"])

            print("Database connection is established...")

            self.cursor = self.connection.cursor(cursor_factory=self.psycopg_cursor_factory)
            self.cursor.executemany(query, variables)
            self.connection.commit()

            return self.cursor.rowcount
        except (Exception, psycopg2.Error) as error:
            print("Database connection error", error)

            self.connection.rollback()
        finally:
            if self.connection is not None:
                self.cursor.close()
                self.connection.close()

                print("Database connection is closed...")
