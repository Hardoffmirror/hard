"""
Currency Tracker
Main module for tracking currency prices and calculating profitability
"""

import logging
from threading import Thread, Event
import time
from typing import Dict
from src.api.poe_ninja_client import PoeNinjaClient
from src.api.poe_trade_client import PoeTradeClient
import config

logger = logging.getLogger(__name__)


class CurrencyTracker:
    """Tracks currency prices and updates database"""

    def __init__(self, db_manager):
        """
        Initialize currency tracker

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.poe_ninja = PoeNinjaClient()
        self.poe_trade = PoeTradeClient()

        self.current_rates = {}
        self.is_running = False
        self.stop_event = Event()
        self.update_thread = None

        logger.info("Currency tracker initialized")

    def start(self):
        """Start tracking currency prices"""
        if self.is_running:
            logger.warning("Tracker already running")
            return

        self.is_running = True
        self.stop_event.clear()

        # Initial fetch
        self.fetch_prices()

        # Start update thread
        self.update_thread = Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()

        logger.info("Currency tracker started")

    def stop(self):
        """Stop tracking currency prices"""
        if not self.is_running:
            return

        self.is_running = False
        self.stop_event.set()

        if self.update_thread:
            self.update_thread.join(timeout=5)

        logger.info("Currency tracker stopped")

    def _update_loop(self):
        """Background update loop"""
        while not self.stop_event.is_set():
            try:
                time.sleep(config.UPDATE_INTERVAL)
                if not self.stop_event.is_set():
                    self.fetch_prices()
            except Exception as e:
                logger.error(f"Error in update loop: {e}")

    def fetch_prices(self):
        """Fetch current prices from API"""
        try:
            logger.info("Fetching currency prices...")

            # Get data from poe.ninja
            currencies = self.poe_ninja.get_all_currencies()

            if not currencies:
                logger.warning("No currency data received")
                return

            # Calculate additional profitability metrics
            currencies = self._calculate_profitability(currencies)

            # Update current rates
            self.current_rates = currencies

            # Save to database
            self.db_manager.save_price_snapshot(currencies)

            logger.info(f"Successfully fetched {len(currencies)} currencies")

        except Exception as e:
            logger.error(f"Failed to fetch prices: {e}")

    def _calculate_profitability(self, currencies: Dict) -> Dict:
        """
        Calculate profitability metrics for currencies

        Args:
            currencies (dict): Currency data

        Returns:
            dict: Updated currency data with profitability metrics
        """
        # Get historical data for comparison
        history = self.db_manager.get_all_currencies_history(days=7)

        for currency_name, data in currencies.items():
            # Calculate trend based on history
            if currency_name in history and len(history[currency_name]) > 0:
                hist_data = history[currency_name]

                # Calculate average price over period
                avg_price = sum(h['chaos_value'] for h in hist_data) / len(hist_data)

                # Calculate volatility
                current_price = data['chaosEquivalent']
                if avg_price > 0:
                    price_deviation = abs(current_price - avg_price) / avg_price * 100
                    data['volatility'] = price_deviation

                # Trend analysis
                if len(hist_data) >= 2:
                    old_price = hist_data[0]['chaos_value']
                    if old_price > 0:
                        trend = ((current_price - old_price) / old_price) * 100
                        data['trend'] = trend

        return currencies

    def get_current_rates(self) -> Dict:
        """
        Get current exchange rates

        Returns:
            dict: Current rates
        """
        # If no data, try to fetch
        if not self.current_rates:
            # Try to get from database first
            self.current_rates = self.db_manager.get_latest_prices()

            # If still no data, fetch from API
            if not self.current_rates:
                self.fetch_prices()

        return self.current_rates

    def get_currency_info(self, currency_name: str) -> Dict:
        """
        Get detailed info for specific currency

        Args:
            currency_name (str): Currency name

        Returns:
            dict: Currency information
        """
        rates = self.get_current_rates()
        return rates.get(currency_name, {})

    def get_top_profitable(self, limit: int = 10) -> list:
        """
        Get top profitable currencies

        Args:
            limit (int): Number of currencies to return

        Returns:
            list: List of (currency_name, profitability) tuples
        """
        rates = self.get_current_rates()

        # Sort by profitability
        sorted_currencies = sorted(
            rates.items(),
            key=lambda x: x[1].get('profitability', 0),
            reverse=True
        )

        return [
            (name, data['profitability'])
            for name, data in sorted_currencies[:limit]
            if data.get('profitability', 0) > config.MIN_PROFIT_PERCENTAGE
        ]

    def test_api_connection(self) -> bool:
        """
        Test API connection

        Returns:
            bool: True if connection successful
        """
        return self.poe_ninja.test_connection()
