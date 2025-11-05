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

    def get_available_leagues(self):
        """
        Get list of available leagues from poe.ninja

        Returns:
            list: List of league names
        """
        try:
            # poe.ninja endpoint that returns economy state including leagues
            url = "https://poe.ninja/api/data/getindexstate"
            params = {'league': 'Standard', 'type': 'Currency'}

            response = self.session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()

            # Extract unique league names from the economy leagues
            leagues = []
            if 'economyLeagues' in data:
                for league_data in data['economyLeagues']:
                    league_name = league_data.get('name', '')
                    if league_name and league_name not in leagues:
                        leagues.append(league_name)

            # If API doesn't return leagues, provide default list
            if not leagues:
                leagues = ['Standard', 'Hardcore', 'Challenge', 'Hardcore Challenge']
                logger.warning("Could not fetch leagues from API, using defaults")

            logger.info(f"Found {len(leagues)} leagues: {leagues}")
            return leagues

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch available leagues: {e}")
            # Return common leagues as fallback
            return ['Standard', 'Hardcore', 'Settlers', 'Hardcore Settlers']

    def get_unique_items(self, league=None):
        """
        Get unique item prices from poe.ninja

        Args:
            league (str): League name

        Returns:
            dict: Unique item prices keyed by item name
        """
        if league is None:
            league = config.CURRENT_LEAGUE

        try:
            url = f"{self.base_url}/itemoverview"

            # poe.ninja has multiple categories for uniques
            categories = ['unique-weapon', 'unique-armour', 'unique-accessory', 'unique-jewel']
            all_items = {}

            for category in categories:
                params = {
                    'league': league,
                    'type': category
                }

                response = self.session.get(
                    url,
                    params=params,
                    timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()

                data = response.json()

                if 'lines' in data:
                    for item in data['lines']:
                        item_name = item.get('name', 'Unknown')
                        chaos_value = item.get('chaosValue', 0)

                        all_items[item_name] = {
                            'chaosValue': chaos_value,
                            'divineValue': item.get('divineValue', 0),
                            'category': category,
                            'icon': item.get('icon', ''),
                            'links': item.get('links', 0),
                            'variant': item.get('variant', None),
                            'itemClass': item.get('itemClass', 0),
                        }

            logger.info(f"Fetched prices for {len(all_items)} unique items")
            return all_items

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch unique item prices: {e}")
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
        Get currency data (only Currency type, no fragments)

        Args:
            league (str): League name

        Returns:
            dict: Currency data
        """
        # Only fetch Currency type, not fragments
        currencies = self.get_currency_overview(league)
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
