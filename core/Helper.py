import json
import os

import requests


def currency_converter(amount, from_currency):
    if from_currency == 'USD':
        return amount

    app_id = os.environ["OPEN_EXCHANGE_APP_ID"]
    url = f"https://openexchangerates.org/api/latest.json/?app_id={app_id}"
    result = requests.get(url)

    if result.status_code == 200:
        rates = json.loads(result.content)['rates']
        if from_currency in rates:
            return float(amount) / float(rates[from_currency])
    return None
