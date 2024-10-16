from datetime import datetime, date
from typing import Optional
import json

from dateutil.parser import isoparse
import requests
import pytz

GAS = 'gas'
ELECTRICITY = 'electricity'

API_ENDPOINT = 'https://frankenergie.be/graphql'
QUERY = '''query MarketPrices($date: String!) {
  marketPrices(date: $date) {
    electricityPrices {
      from
      till
      marketPrice
    }
    gasPrices {
      from
      till
      marketPrice
    }
  }
}
'''

JSON_DATA = {'query': QUERY, 'operationName': 'MarketPrices'}


class EnergyPrice:

    def __init__(self):
        self._last_query = None
        self.data: dict[date, dict[str, list[tuple[datetime, datetime, float]]]] = dict()

    def _poll_server_day_data(self, day: date) -> dict[str, list[tuple[datetime, datetime, float]]]:
        # Data gets requests day in Europe/Brussels put returns in UTC time
        variables = {'variables': {'date': day.strftime('%Y-%m-%d')}}
        response = requests.post(url=API_ENDPOINT,
                                 json=JSON_DATA | variables,
                                 headers={'x-country': 'BE'},
                                 )
        json_response = response.json()['data']['marketPrices']
        print(json.dumps(json_response, indent=4))
        return {ELECTRICITY: self._parse_data(json_response['electricityPrices']),
                GAS: self._parse_data(json_response['gasPrices'])}

    @staticmethod
    def _parse_data(json_data) -> list[tuple[datetime, datetime, float]]:
        return [(isoparse(x['from']), isoparse(x['till']), x['marketPrice']) for x in json_data]

    def get_hourly_price(self, entity: str, timestamp: Optional[datetime] = None) -> float:
        if timestamp is None:
            timestamp = datetime.now(tz=pytz.timezone('Europe/Brussels'))
        day_data = self.get_day_data(timestamp.date())[entity]

        timestamp = timestamp.astimezone(tz=pytz.timezone('UTC'))
        for start, end, price in day_data:
            if start <= timestamp < end:
                return price
        raise ValueError(f'Could not get price for {timestamp}.')

    def get_day_data(self, day: date):
        if day not in self.data:
            self.data[day] = self._poll_server_day_data(day)
        return self.data[day]


def print_local_day_prices(price: EnergyPrice, entity: str):
    today = datetime.today()
    for h in range(24):
        hour = today.replace(hour=h, minute=0, second=0, microsecond=0)
        print(f'{hour}:\t{price.get_hourly_price(entity, hour):.3f}')


if __name__ == '__main__':
    frank_prices = EnergyPrice()
    print('Gas:')
    print_local_day_prices(frank_prices, GAS)

    print('\n\nElectricity:')
    print_local_day_prices(frank_prices, ELECTRICITY)
