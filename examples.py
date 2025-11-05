#!/usr/bin/env python3
"""
Examples of using PoE Currency Exchange Helper programmatically
"""

from src.database.db_manager import DatabaseManager
from src.core.currency_tracker import CurrencyTracker
from src.core.profit_calculator import ProfitCalculator
from src.api.poe_ninja_client import PoeNinjaClient
from src.utils.chart_generator import ChartGenerator


def example_fetch_prices():
    """Example: Fetch current currency prices"""
    print("=== Fetching Currency Prices ===\n")

    client = PoeNinjaClient()
    currencies = client.get_all_currencies()

    print(f"Fetched {len(currencies)} currencies:\n")

    # Show top 10 by value
    sorted_currencies = sorted(
        currencies.items(),
        key=lambda x: x[1].get('chaosEquivalent', 0),
        reverse=True
    )[:10]

    for name, data in sorted_currencies:
        chaos_value = data.get('chaosEquivalent', 0)
        change = data.get('change24h', 0)
        print(f"{name:30} {chaos_value:8.2f}c  ({change:+.2f}%)")


def example_calculate_profit():
    """Example: Calculate exchange profitability"""
    print("\n=== Calculate Exchange Profit ===\n")

    db_manager = DatabaseManager(":memory:")  # Use in-memory DB for example
    tracker = CurrencyTracker(db_manager)
    calculator = ProfitCalculator(db_manager)

    # Fetch current rates
    tracker.fetch_prices()
    rates = tracker.get_current_rates()

    # Calculate exchange: 100 Chaos -> Divine
    result = calculator.calculate_exchange_profit(
        have="Chaos Orb",
        want="Divine Orb",
        have_amount=100,
        currency_rates=rates
    )

    print(f"Exchange 100 Chaos Orb for Divine Orb:")
    print(f"  You will receive: {result.get('want_amount', 0):.2f} Divine Orbs")
    print(f"  Profitability: {result.get('profit_percentage', 0):.2f}%")
    print(f"  Recommendation: {result.get('recommendation', 'N/A')}")


def example_find_arbitrage():
    """Example: Find arbitrage opportunities"""
    print("\n=== Finding Arbitrage Opportunities ===\n")

    db_manager = DatabaseManager(":memory:")
    tracker = CurrencyTracker(db_manager)
    calculator = ProfitCalculator(db_manager)

    # Fetch current rates
    tracker.fetch_prices()
    rates = tracker.get_current_rates()

    # Find opportunities
    opportunities = calculator.find_arbitrage_opportunities(
        rates,
        min_profit=3.0
    )

    print(f"Found {len(opportunities)} opportunities:\n")

    for i, opp in enumerate(opportunities[:5], 1):
        print(f"{i}. {opp['path']:40} {opp['profit']:6.2f}% profit")


def example_price_history():
    """Example: Work with price history"""
    print("\n=== Price History ===\n")

    db_manager = DatabaseManager()
    tracker = CurrencyTracker(db_manager)

    # Fetch and save prices
    tracker.fetch_prices()

    # Get history for a currency
    history = db_manager.get_price_history("Divine Orb", days=7)

    print(f"Divine Orb price history ({len(history)} records):\n")

    for record in history[-5:]:  # Last 5 records
        timestamp = record['timestamp'][:19]  # Truncate timestamp
        chaos_value = record['chaos_value']
        change = record.get('change_24h', 0)
        print(f"{timestamp}  {chaos_value:8.2f}c  ({change:+.2f}%)")

    db_manager.close()


def example_generate_chart():
    """Example: Generate price chart"""
    print("\n=== Generating Chart ===\n")

    db_manager = DatabaseManager()
    tracker = CurrencyTracker(db_manager)
    chart_gen = ChartGenerator()

    # Fetch data
    tracker.fetch_prices()

    # Get history
    history = db_manager.get_price_history("Divine Orb", days=7)

    if history:
        # Generate chart
        chart_data = chart_gen.create_price_history_chart(history, "Divine Orb")

        # Save to file
        chart_gen.save_chart(chart_data, "divine_orb_chart.png")
        print("Chart saved to divine_orb_chart.png")
    else:
        print("No historical data available")

    db_manager.close()


def example_statistics():
    """Example: Get trading statistics"""
    print("\n=== Trading Statistics ===\n")

    db_manager = DatabaseManager()

    # Record some example trades
    db_manager.record_trade("Divine Orb", "BUY", 5.5, "Good deal")
    db_manager.record_trade("Exalted Orb", "SELL", 3.2, "Quick flip")
    db_manager.record_trade("Mirror of Kalandra", "BUY", 15.0, "Long term hold")

    # Get statistics
    stats = db_manager.get_statistics()

    print(f"Total trades: {stats['total_trades']}")
    print(f"Most profitable currency: {stats['most_profitable']}")
    print(f"Average profit: {stats['avg_profit']:.2f}%")
    print(f"Best trading time: {stats['best_time']}")

    db_manager.close()


def example_multi_hop_profit():
    """Example: Calculate multi-step exchange profit"""
    print("\n=== Multi-hop Exchange ===\n")

    db_manager = DatabaseManager(":memory:")
    tracker = CurrencyTracker(db_manager)
    calculator = ProfitCalculator(db_manager)

    # Fetch rates
    tracker.fetch_prices()
    rates = tracker.get_current_rates()

    # Calculate multi-hop path
    path = ["Chaos Orb", "Exalted Orb", "Divine Orb"]
    result = calculator.calculate_multi_hop_profit(
        path,
        start_amount=100,
        currency_rates=rates
    )

    print(f"Path: {result.get('path', 'N/A')}")
    print(f"Start: {result.get('start_amount', 0)} Chaos Orbs")
    print(f"End: {result.get('final_amount', 0):.4f} {result.get('final_currency', '')}")
    print(f"Total profit: {result.get('total_profit_percentage', 0):.2f}%")
    print(f"Recommendation: {result.get('recommendation', 'N/A')}")


def example_best_time_to_trade():
    """Example: Analyze best trading time"""
    print("\n=== Best Time to Trade ===\n")

    db_manager = DatabaseManager()
    tracker = CurrencyTracker(db_manager)
    calculator = ProfitCalculator(db_manager)

    # Fetch and save some data
    tracker.fetch_prices()

    # Analyze best time
    result = calculator.get_best_time_to_trade("Divine Orb", days=7)

    if 'error' not in result:
        print(f"Currency: {result['currency']}")
        print(f"Best hour to trade: {result['best_hour']}")
        print(f"Avg profit at best hour: {result['avg_profit_at_best_hour']:.2f}%")
    else:
        print(f"Error: {result['error']}")

    db_manager.close()


if __name__ == "__main__":
    print("PoE Currency Exchange Helper - Examples\n")
    print("=" * 60)

    try:
        example_fetch_prices()
        example_calculate_profit()
        example_find_arbitrage()
        example_price_history()
        example_statistics()
        example_multi_hop_profit()
        example_generate_chart()
        example_best_time_to_trade()

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have internet connection and all dependencies installed.")

    print("\n" + "=" * 60)
    print("Examples completed!")
