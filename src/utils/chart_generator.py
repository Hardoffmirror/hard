"""
Chart Generator
Creates price charts and visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import io
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Set matplotlib to use non-interactive backend
plt.switch_backend('Agg')


class ChartGenerator:
    """Generate charts for currency data"""

    def __init__(self):
        """Initialize chart generator"""
        # Set style
        plt.style.use('dark_background')

    def create_price_history_chart(self, history_data: List[Dict],
                                     currency_name: str) -> bytes:
        """
        Create price history line chart

        Args:
            history_data (list): List of price history records
            currency_name (str): Currency name for title

        Returns:
            bytes: PNG image data
        """
        if not history_data:
            return self._create_empty_chart("No data available")

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Extract data
            timestamps = [datetime.fromisoformat(d['timestamp']) for d in history_data]
            prices = [d['chaos_value'] for d in history_data]

            # Plot
            ax.plot(timestamps, prices, color='#FFD700', linewidth=2, marker='o', markersize=4)

            # Formatting
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Chaos Orb Value', fontsize=12)
            ax.set_title(f'{currency_name} Price History', fontsize=14, fontweight='bold')

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            plt.xticks(rotation=45)

            # Grid
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e')
            buf.seek(0)
            plt.close()

            return buf.getvalue()

        except Exception as e:
            logger.error(f"Failed to create price chart: {e}")
            return self._create_empty_chart("Error creating chart")

    def create_profitability_chart(self, currency_data: Dict) -> bytes:
        """
        Create profitability comparison bar chart

        Args:
            currency_data (dict): Dictionary of currency data

        Returns:
            bytes: PNG image data
        """
        if not currency_data:
            return self._create_empty_chart("No data available")

        try:
            # Sort by profitability
            sorted_data = sorted(
                currency_data.items(),
                key=lambda x: x[1].get('profitability', 0),
                reverse=True
            )[:15]  # Top 15

            currencies = [name[:20] for name, _ in sorted_data]  # Truncate names
            profits = [data.get('profitability', 0) for _, data in sorted_data]

            # Create chart
            fig, ax = plt.subplots(figsize=(12, 8))

            colors = ['#00FF00' if p > 5 else '#FFD700' if p > 0 else '#FF0000' for p in profits]
            bars = ax.barh(currencies, profits, color=colors)

            # Formatting
            ax.set_xlabel('Profitability (%)', fontsize=12)
            ax.set_title('Currency Profitability Comparison', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')

            # Add value labels
            for i, (bar, profit) in enumerate(zip(bars, profits)):
                ax.text(profit + 0.1, i, f'{profit:.2f}%', va='center')

            plt.tight_layout()

            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e')
            buf.seek(0)
            plt.close()

            return buf.getvalue()

        except Exception as e:
            logger.error(f"Failed to create profitability chart: {e}")
            return self._create_empty_chart("Error creating chart")

    def create_trend_chart(self, history_dict: Dict[str, List[Dict]]) -> bytes:
        """
        Create multi-currency trend comparison chart

        Args:
            history_dict (dict): Dictionary with currency names as keys

        Returns:
            bytes: PNG image data
        """
        if not history_dict:
            return self._create_empty_chart("No data available")

        try:
            fig, ax = plt.subplots(figsize=(12, 8))

            colors = ['#FFD700', '#00FF00', '#FF00FF', '#00FFFF', '#FF6600']

            for i, (currency_name, history) in enumerate(list(history_dict.items())[:5]):
                if not history:
                    continue

                timestamps = [datetime.fromisoformat(d['timestamp']) for d in history]
                prices = [d['chaos_value'] for d in history]

                # Normalize to percentage change
                if prices and prices[0] > 0:
                    normalized = [(p / prices[0] - 1) * 100 for p in prices]
                    ax.plot(timestamps, normalized,
                           label=currency_name[:20],
                           color=colors[i % len(colors)],
                           linewidth=2)

            # Formatting
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Price Change (%)', fontsize=12)
            ax.set_title('Currency Price Trends Comparison', fontsize=14, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)

            # Add zero line
            ax.axhline(y=0, color='white', linestyle='--', alpha=0.5)

            plt.tight_layout()

            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e')
            buf.seek(0)
            plt.close()

            return buf.getvalue()

        except Exception as e:
            logger.error(f"Failed to create trend chart: {e}")
            return self._create_empty_chart("Error creating chart")

    def create_volatility_chart(self, currency_data: Dict) -> bytes:
        """
        Create volatility scatter chart

        Args:
            currency_data (dict): Currency data with volatility info

        Returns:
            bytes: PNG image data
        """
        try:
            # Extract volatility data
            data_points = [
                (name, data.get('chaosEquivalent', 0), data.get('volatility', 0))
                for name, data in currency_data.items()
                if 'volatility' in data
            ]

            if not data_points:
                return self._create_empty_chart("No volatility data available")

            names, values, volatilities = zip(*data_points)

            fig, ax = plt.subplots(figsize=(12, 8))

            # Scatter plot
            scatter = ax.scatter(values, volatilities, c=volatilities,
                                cmap='RdYlGn_r', s=100, alpha=0.6)

            # Formatting
            ax.set_xlabel('Chaos Value', fontsize=12)
            ax.set_ylabel('Volatility (%)', fontsize=12)
            ax.set_title('Currency Volatility vs Value', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Add colorbar
            plt.colorbar(scatter, label='Volatility')

            # Annotate high-value currencies
            for name, val, vol in data_points[:10]:
                ax.annotate(name[:15], (val, vol), fontsize=8, alpha=0.7)

            plt.tight_layout()

            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e')
            buf.seek(0)
            plt.close()

            return buf.getvalue()

        except Exception as e:
            logger.error(f"Failed to create volatility chart: {e}")
            return self._create_empty_chart("Error creating chart")

    def _create_empty_chart(self, message: str) -> bytes:
        """
        Create empty chart with message

        Args:
            message (str): Message to display

        Returns:
            bytes: PNG image data
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, message,
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                fontsize=16)
        ax.set_xticks([])
        ax.set_yticks([])

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#1e1e1e')
        buf.seek(0)
        plt.close()

        return buf.getvalue()

    def save_chart(self, chart_data: bytes, filename: str):
        """
        Save chart to file

        Args:
            chart_data (bytes): Chart image data
            filename (str): Output filename
        """
        try:
            with open(filename, 'wb') as f:
                f.write(chart_data)
            logger.info(f"Chart saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save chart: {e}")
