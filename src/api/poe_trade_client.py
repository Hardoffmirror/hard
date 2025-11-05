"""
PoE Trade API Client
For direct trade data (optional, as poe.ninja is more reliable)
"""

import requests
import logging
import config

logger = logging.getLogger(__name__)


class PoeTradeClient:
    """Client for interacting with official PoE Trade API"""

    def __init__(self):
        self.base_url = "https://www.pathofexile.com/api/trade"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PoE-Currency-Exchange-Helper/1.0'
        })

    def search_exchange(self, have, want, league=None):
        """
        Search for currency exchange offers

        Args:
            have (str): Currency you have
            want (str): Currency you want
            league (str): League name

        Returns:
            dict: Search results
        """
        if league is None:
            league = config.CURRENT_LEAGUE

        try:
            url = f"{self.base_url}/exchange/{league}"

            payload = {
                "exchange": {
                    "status": {"option": "online"},
                    "have": [have],
                    "want": [want]
                }
            }

            response = self.session.post(
                url,
                json=payload,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search exchange: {e}")
            return {}

    def fetch_listings(self, query_id, exchange_ids):
        """
        Fetch specific listings by IDs

        Args:
            query_id (str): Query ID from search
            exchange_ids (list): List of exchange IDs

        Returns:
            dict: Listing details
        """
        try:
            # Limit to first 10 exchanges
            ids_str = ','.join(exchange_ids[:10])
            url = f"{self.base_url}/fetch/{ids_str}"

            params = {'query': query_id, 'exchange': True}

            response = self.session.get(
                url,
                params=params,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch listings: {e}")
            return {}

    def get_best_rate(self, have, want, league=None):
        """
        Get best exchange rate for currency pair

        Args:
            have (str): Currency you have
            want (str): Currency you want
            league (str): League name

        Returns:
            float: Best rate or 0 if not found
        """
        search_result = self.search_exchange(have, want, league)

        if not search_result or 'result' not in search_result:
            return 0

        result_ids = search_result.get('result', [])
        if not result_ids:
            return 0

        # Fetch actual listings
        listings = self.fetch_listings(search_result['id'], result_ids)

        if not listings or 'result' not in listings:
            return 0

        # Find best rate
        best_rate = 0
        for listing in listings['result']:
            listing_data = listing.get('listing', {})
            price = listing_data.get('price', {})

            exchange_amount = price.get('exchange', {}).get('amount', 0)
            item_amount = price.get('item', {}).get('amount', 1)

            if item_amount > 0:
                rate = exchange_amount / item_amount
                if rate > best_rate:
                    best_rate = rate

        return best_rate
