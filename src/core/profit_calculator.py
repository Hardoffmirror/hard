"""
Profit Calculator
Calculates profitability of currency exchanges
"""

import logging
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)


class ProfitCalculator:
    """Calculate profit for currency trades"""

    def __init__(self, db_manager):
        """
        Initialize profit calculator

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def calculate_exchange_profit(self, have: str, want: str,
                                   have_amount: float,
                                   currency_rates: Dict) -> Dict:
        """
        Calculate profit for an exchange

        Args:
            have (str): Currency you have
            want (str): Currency you want
            have_amount (float): Amount of currency you have
            currency_rates (dict): Current currency rates

        Returns:
            dict: Profit calculation results
        """
        if have not in currency_rates or want not in currency_rates:
            return {
                'error': 'Currency not found',
                'profit': 0,
                'profit_percentage': 0
            }

        have_data = currency_rates[have]
        want_data = currency_rates[want]

        # Convert to chaos for comparison
        have_chaos_value = have_data.get('chaosEquivalent', 0) * have_amount
        want_chaos_value = want_data.get('chaosEquivalent', 0)

        # Calculate how much of 'want' currency you can get
        want_amount = have_chaos_value / want_chaos_value if want_chaos_value > 0 else 0

        # Calculate actual exchange rate with spreads
        buy_rate = have_data.get('pay', 0)
        sell_rate = want_data.get('receive', 0)

        # Account for spread
        if buy_rate > 0 and sell_rate > 0:
            actual_want_amount = (have_amount * buy_rate) / sell_rate
            spread_loss = (want_amount - actual_want_amount) / want_amount * 100 if want_amount > 0 else 0
        else:
            actual_want_amount = want_amount
            spread_loss = 0

        # Calculate profit percentage
        profitability = have_data.get('profitability', 0) + want_data.get('profitability', 0)

        return {
            'have': have,
            'want': want,
            'have_amount': have_amount,
            'want_amount': actual_want_amount,
            'have_chaos_value': have_chaos_value,
            'want_chaos_value': want_chaos_value * actual_want_amount,
            'profit_percentage': profitability,
            'spread_loss': spread_loss,
            'recommendation': 'GOOD' if profitability > 5 else 'FAIR' if profitability > 0 else 'POOR'
        }

    def find_arbitrage_opportunities(self, currency_rates: Dict,
                                      min_profit: float = 5.0) -> List[Dict]:
        """
        Find arbitrage opportunities between currencies

        Args:
            currency_rates (dict): Current currency rates
            min_profit (float): Minimum profit percentage

        Returns:
            list: List of arbitrage opportunities
        """
        opportunities = []

        currencies = list(currency_rates.keys())

        for i, curr_a in enumerate(currencies):
            for curr_b in currencies[i + 1:]:
                # Calculate both directions
                result_ab = self.calculate_exchange_profit(
                    curr_a, curr_b, 1, currency_rates
                )
                result_ba = self.calculate_exchange_profit(
                    curr_b, curr_a, 1, currency_rates
                )

                # Check for profitable round trip
                if result_ab.get('profit_percentage', 0) >= min_profit:
                    opportunities.append({
                        'from': curr_a,
                        'to': curr_b,
                        'profit': result_ab['profit_percentage'],
                        'path': f"{curr_a} -> {curr_b}"
                    })

                if result_ba.get('profit_percentage', 0) >= min_profit:
                    opportunities.append({
                        'from': curr_b,
                        'to': curr_a,
                        'profit': result_ba['profit_percentage'],
                        'path': f"{curr_b} -> {curr_a}"
                    })

        # Sort by profit
        opportunities.sort(key=lambda x: x['profit'], reverse=True)

        return opportunities[:20]  # Return top 20

    def calculate_multi_hop_profit(self, path: List[str],
                                     start_amount: float,
                                     currency_rates: Dict) -> Dict:
        """
        Calculate profit for multi-step currency exchange

        Args:
            path (list): List of currencies in exchange path
            start_amount (float): Starting amount
            currency_rates (dict): Current currency rates

        Returns:
            dict: Profit calculation
        """
        if len(path) < 2:
            return {'error': 'Path too short'}

        current_currency = path[0]
        current_amount = start_amount

        steps = []

        for next_currency in path[1:]:
            result = self.calculate_exchange_profit(
                current_currency,
                next_currency,
                current_amount,
                currency_rates
            )

            steps.append(result)

            current_currency = next_currency
            current_amount = result.get('want_amount', 0)

        # Calculate total profit
        final_chaos_value = steps[-1].get('want_chaos_value', 0)
        start_chaos_value = currency_rates[path[0]].get('chaosEquivalent', 0) * start_amount

        total_profit = 0
        if start_chaos_value > 0:
            total_profit = ((final_chaos_value - start_chaos_value) / start_chaos_value) * 100

        return {
            'path': ' -> '.join(path),
            'start_amount': start_amount,
            'final_amount': current_amount,
            'final_currency': path[-1],
            'steps': steps,
            'total_profit_percentage': total_profit,
            'recommendation': 'EXCELLENT' if total_profit > 10 else 'GOOD' if total_profit > 5 else 'FAIR'
        }

    def get_best_time_to_trade(self, currency_name: str, days: int = 7) -> Dict:
        """
        Analyze best time to trade based on historical data

        Args:
            currency_name (str): Currency to analyze
            days (int): Days of history to analyze

        Returns:
            dict: Time analysis
        """
        history = self.db_manager.get_price_history(currency_name, days)

        if not history:
            return {'error': 'No historical data'}

        # Analyze by hour
        hour_profits = {}

        for record in history:
            timestamp = record['timestamp']
            hour = timestamp.split('T')[1].split(':')[0]  # Extract hour

            if hour not in hour_profits:
                hour_profits[hour] = []

            hour_profits[hour].append(record.get('profitability', 0))

        # Calculate average by hour
        hour_averages = {
            hour: sum(profits) / len(profits)
            for hour, profits in hour_profits.items()
        }

        best_hour = max(hour_averages.items(), key=lambda x: x[1])

        return {
            'currency': currency_name,
            'best_hour': f"{best_hour[0]}:00",
            'avg_profit_at_best_hour': best_hour[1],
            'hour_averages': hour_averages
        }
