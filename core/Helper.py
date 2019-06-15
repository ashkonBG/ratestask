import json
import requests


def currency_converter(amount, from_currency):
    if from_currency == 'USD':
        return amount

    url = f"https://openexchangerates.org/api/latest.json/" \
        f"?app_id=79bad99488a847e7b8b77f246714ed5a"
    result = requests.get(url)

    if result.status_code == 200:
        rates = json.loads(result.content)['rates']
        if from_currency in rates:
            return float(amount) / float(rates[from_currency])
    return None
