from datetime import datetime, timedelta
from logging import FileHandler, ERROR

import psycopg2.extras
from flask import Flask, request, jsonify, make_response

from core.DB import DB
from core.Helper import currency_converter
from core.Validator import Validator

app = Flask(__name__)

file_handler = FileHandler('log.txt')
file_handler.setLevel(ERROR)
app.logger.addHandler(file_handler)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'code': 404, 'message': 'The requested route is not found.'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'code': 500, 'message': 'Internal server Error.'}), 500)


# Routes
@app.route('/rates/', methods=['GET', 'POST'])
def rates_func():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    price = request.args.get('price')
    currency = request.args.get('currency')

    if request.method == "GET":
        validator = Validator()
        validator.is_date('date_from', date_from)
        validator.is_date('date_to', date_to)
        validator.is_valid_date_range('date_from', 'date_to', date_from, date_to)
        validator.is_not_empty('origin', origin)
        validator.is_not_empty('destination', destination)

        errors = validator.get_errors()

        if errors:
            return jsonify({'code': 422, 'message': errors}), 422

            db = DB(psycopg2.extras.RealDictCursor)
            rows = db.get_rows(
                """
                SELECT to_char(day, 'YYYY-MM-DD')         AS day,
                       ROUND(AVG(price)) :: bigint AS average_price
                FROM prices
                WHERE day BETWEEN %(date_from)s AND %(date_to)s
                  AND (orig_code = %(origin)s
                    OR orig_code IN (SELECT code FROM ports WHERE parent_slug = %(origin)s)
                    OR orig_code IN (SELECT code FROM ports WHERE parent_slug IN (SELECT slug FROM regions WHERE parent_slug = %(origin)s)))
                  AND (dest_code = %(destination)s
                    OR dest_code IN (SELECT code FROM ports WHERE parent_slug = %(destination)s)
                    OR dest_code IN (SELECT code FROM ports WHERE parent_slug IN (SELECT slug FROM regions WHERE parent_slug = %(destination)s)))
                GROUP BY day
                ORDER BY day ASC
                """,
                {
                    "date_from": date_from,
                    "date_to": date_to,
                    "origin": origin,
                    "destination": destination,
                })
            return jsonify({'success': True, 'data': rows}), 200

    if request.method == "POST":
        validator = Validator()
        validator.is_date('date_from', date_from)
        validator.is_date('date_to', date_to)
        validator.is_valid_date_range('date_from', 'date_to', date_from, date_to)
        validator.is_not_empty('origin', origin)
        validator.exists_in_table('origin', origin, 'ports', 'code')
        validator.is_not_empty('destination', destination)
        validator.exists_in_table('destination', destination, 'ports', 'code')
        validator.is_not_empty('price', price)
        validator.is_number('price', price)
        if currency is not None:
            validator.is_valid_currency('currency', currency)

        errors = validator.get_errors()

        if errors:
            return jsonify({'code': 422, 'message': errors}), 422

        if currency is not None:
            converted_price = currency_converter(price, currency)

            if converted_price is None:
                return make_response(jsonify({'code': 500, 'message': 'An unknown error has occurred.'}), 500)

            price = round(float(converted_price))

        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        date_list = [date_from + timedelta(days=x) for x in range(0, (date_to - date_from).days)]
        date_list.append(date_to)

        query_values = []

        for date in date_list:
            query_values.append((origin, destination, date.strftime('%Y-%m-%d'), price))

        db = DB(psycopg2.extras.RealDictCursor)
        count = db.insert_rows(
            """
            INSERT INTO prices (orig_code, dest_code, day, price)
            VALUES (%s, %s, %s, %s)
            """,
            query_values
        )

        return jsonify({'success': True, 'message': '{} record(s) inserted.'.format(count)}), 200


@app.route('/rates_null/', methods=['GET'])
def rates_null_func():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    validator = Validator()
    validator.is_date('date_from', date_from)
    validator.is_date('date_to', date_to)
    validator.is_valid_date_range('date_from', 'date_to', date_from, date_to)
    validator.is_not_empty('origin', origin)
    validator.is_not_empty('destination', destination)
    errors = validator.get_errors()

    if errors:
        return jsonify({'code': 422, 'message': errors}), 422

    db = DB(psycopg2.extras.RealDictCursor)
    rows = db.get_rows(
        """
        SELECT to_char(day, 'YYYY-MM-DD')         AS day,
               (CASE WHEN COUNT(*) > 3 THEN ROUND(AVG(price)) :: bigint END) AS average_price
        FROM prices
        WHERE day BETWEEN %(date_from)s AND %(date_to)s
          AND (orig_code = %(origin)s
            OR orig_code IN (SELECT code FROM ports WHERE parent_slug = %(origin)s)
            OR orig_code IN (SELECT code FROM ports WHERE parent_slug IN (SELECT slug FROM regions WHERE parent_slug = %(origin)s)))
          AND (dest_code = %(destination)s
            OR dest_code IN (SELECT code FROM ports WHERE parent_slug = %(destination)s)
            OR dest_code IN (SELECT code FROM ports WHERE parent_slug IN (SELECT slug FROM regions WHERE parent_slug = %(destination)s)))
        GROUP BY day
        ORDER BY day ASC
        """,
        {
            "date_from": date_from,
            "date_to": date_to,
            "origin": origin,
            "destination": destination,
        })

    return jsonify({'success': True, 'data': rows})


if __name__ == '__main__':
    app.run()
