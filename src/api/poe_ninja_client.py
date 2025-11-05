"""
PoE.ninja API Client
Fetches currency exchange rates from poe.ninja
"""

import requests
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class PoeNinjaClient:
    """Client for interacting with poe.ninja API"""

    def __init__(self):
        self.base_url = "https://poe.ninja/api/data"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PoE-Currency-Exchange-Helper/1.0'
        })

    def get_currency_overview(self, league=None):
        """
        Get currency overview data

        Args:
            league (str): League name, defaults to config.CURRENT_LEAGUE

        Returns:
            dict: Currency data or empty dict on error
        """
        if league is None:
            league = config.CURRENT_LEAGUE

        try:
            url = f"{self.base_url}/currencyoverview"
            params = {
                'league': league,
                'type': 'Currency'
            }

            response = self.session.get(
                url,
                params=params,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            return self._process_currency_data(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch currency data: {e}")
            return {}

    def get_fragment_overview(self, league=None):
        """
        Get fragment overview data (for special currencies)

        Args:
            league (str): League name

        Returns:
            dict: Fragment data or empty dict on error
        """
        if league is None:
            league = config.CURRENT_LEAGUE

        try:
            url = f"{self.base_url}/currencyoverview"
            params = {
                'league': league,
                'type': 'Fragment'
            }

            response = self.session.get(
                url,
                params=params,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch fragment data: {e}")
            return {}

    def _process_currency_data(self, raw_data):
        """
        Process raw API data into structured format

        Args:
            raw_data (dict): Raw API response

        Returns:
            dict: Processed currency data
        """
        processed = {}

        if 'lines' not in raw_data:
            return processed

        for item in raw_data['lines']:
            currency_name = item.get('currencyTypeName', 'Unknown')

            # Extract key data
            chaos_value = item.get('chaosEquivalent', 0)

            # Get price history for trend calculation
            receive_data = item.get('receiveSparkLine', {}).get('data', [])

            # Calculate 24h change
            change_24h = 0
            if len(receive_data) >= 2:
                current = receive_data[-1] if receive_data[-1] else chaos_value
                previous = receive_data[0] if receive_data[0] else chaos_value
                if previous > 0:
                    change_24h = ((current - previous) / previous) * 100

            # Calculate profitability (difference between buy and sell)
            pay_value = item.get('pay', {}).get('value', 0)
            receive_value = item.get('receive', {}).get('value', 0)

            profitability = 0
            if receive_value > 0 and pay_value > 0:
                # Calculate spread percentage
                profitability = ((receive_value - pay_value) / pay_value) * 100

            processed[currency_name] = {
                'chaosEquivalent': chaos_value,
                'change24h': change_24h,
                'profitability': profitability,
                'pay': pay_value,
                'receive': receive_value,
                'lowConfidence': item.get('lowConfidenceSparkLine', {}).get('totalChange', 0),
                'detailsId': item.get('detailsId', ''),
                'timestamp': datetime.now().isoformat()
            }

        return processed

    def get_all_currencies(self, league=None):
        """
        Get all currency data including both standard and fragments

        Args:
            league (str): League name

        Returns:
            dict: Combined currency data
        """
        currencies = self.get_currency_overview(league)
        fragments = self.get_fragment_overview(league)

        # Combine both datasets
        if fragments and 'lines' in fragments:
            fragment_data = self._process_currency_data(fragments)
            currencies.update(fragment_data)

        return currencies

    def test_connection(self):
        """
        Test API connection

        Returns:
            bool: True if connection successful
        """
        try:
            response = self.session.get(
                f"{self.base_url}/currencyoverview",
                params={'league': 'Standard', 'type': 'Currency'},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
