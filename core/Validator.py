import json
from datetime import datetime

import psycopg2.extras

from core.DB import DB


class Validator:
    def __init__(self) -> None:
        self.errors = {}

    def is_not_empty(self, attribute_name, value):
        if value is None or not value.strip():
            self.errors[attribute_name] = "{} can not be empty.".format(attribute_name)
            return False
        return True

    def is_date(self, attribute_name, date_text, date_format='%Y-%m-%d', display_date_format='YYYY-MM-DD'):
        if self.is_not_empty(attribute_name, date_text):
            try:
                if date_text != datetime.strptime(date_text, date_format).strftime(date_format):
                    raise ValueError
                return True
            except ValueError:
                self.errors[attribute_name] = "'{}' is not a valid date (valid format: {}).".format(date_text,
                                                                                                    display_date_format)
                return False
        return False

    def is_valid_date_range(self, attribute_name_date_from, attribute_name_date_to, date_from, date_to,
                            date_format='%Y-%m-%d'):
        if self.is_date(attribute_name_date_from, date_from) and self.is_date(attribute_name_date_to, date_to):
            if datetime.strptime(date_from, date_format) <= datetime.strptime(date_to, date_format):
                return True
            self.errors[attribute_name_date_from] = "{} can not be greater than {}.".format(attribute_name_date_from,
                                                                                            attribute_name_date_to)
            self.errors[attribute_name_date_to] = "{} can not be less than {}.".format(attribute_name_date_to,
                                                                                       attribute_name_date_from)
            return False
        return False

    def is_valid_currency(self, attribute_name, value):
        if self.is_not_empty(attribute_name, value):
            with open('currencies.json') as json_file:
                currencies = json.load(json_file)
                if value not in currencies:
                    self.errors[attribute_name] = "{} is not valid (valid e.g. USD).".format(attribute_name)
                    return False
                return True
        return False

    def exists_in_table(self, attribute_name, value, table, column):
        if self.is_not_empty(attribute_name, value):
            db = DB(psycopg2.extras.RealDictCursor)
            if db.dynamic_get_row(table, column, value):
                return True
            self.errors[attribute_name] = "{} is not a valid port code.".format(value)
            return False
        return False

    def is_number(self, attribute_name, value):
        if self.is_not_empty(attribute_name, value):
            if value.isnumeric():
                return True
            try:
                float(value)
            except ValueError:
                self.errors[attribute_name] = "{} is not a number.".format(value)
                return False
        return False

    def get_errors(self):
        return list(self.errors.values())
