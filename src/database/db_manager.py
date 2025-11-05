"""
Database Manager
Handles all database operations for price history and statistics
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for currency tracking"""

    def __init__(self, db_path=None):
        """
        Initialize database manager

        Args:
            db_path (str): Path to database file
        """
        self.db_path = db_path or config.DB_NAME
        self.connection = None
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()

        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_name TEXT NOT NULL,
                chaos_value REAL NOT NULL,
                change_24h REAL,
                profitability REAL,
                pay_value REAL,
                receive_value REAL,
                timestamp TEXT NOT NULL,
                league TEXT NOT NULL
            )
        """)

        # Trade statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_name TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                profit REAL,
                trade_date TEXT NOT NULL,
                notes TEXT
            )
        """)

        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_currency
            ON price_history(currency_name, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_date
            ON trade_statistics(trade_date)
        """)

        self.connection.commit()
        logger.info("Database initialized successfully")

    def save_price_snapshot(self, currency_data: Dict, league: str = None):
        """
        Save current price snapshot to database

        Args:
            currency_data (dict): Dictionary of currency data
            league (str): League name
        """
        if league is None:
            league = config.CURRENT_LEAGUE

        cursor = self.connection.cursor()

        for currency_name, data in currency_data.items():
            cursor.execute("""
                INSERT INTO price_history
                (currency_name, chaos_value, change_24h, profitability,
                 pay_value, receive_value, timestamp, league)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                currency_name,
                data.get('chaosEquivalent', 0),
                data.get('change24h', 0),
                data.get('profitability', 0),
                data.get('pay', 0),
                data.get('receive', 0),
                data.get('timestamp', datetime.now().isoformat()),
                league
            ))

        self.connection.commit()
        logger.info(f"Saved price snapshot for {len(currency_data)} currencies")

    def get_price_history(self, currency_name: str, days: int = 7) -> List[Dict]:
        """
        Get price history for a specific currency

        Args:
            currency_name (str): Name of the currency
            days (int): Number of days to retrieve

        Returns:
            list: List of price records
        """
        cursor = self.connection.cursor()

        start_date = datetime.now() - timedelta(days=days)

        cursor.execute("""
            SELECT currency_name, chaos_value, change_24h,
                   profitability, timestamp
            FROM price_history
            WHERE currency_name = ?
            AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (currency_name, start_date.isoformat()))

        rows = cursor.fetchall()

        return [
            {
                'currency_name': row[0],
                'chaos_value': row[1],
                'change_24h': row[2],
                'profitability': row[3],
                'timestamp': row[4]
            }
            for row in rows
        ]

    def get_all_currencies_history(self, days: int = 7) -> Dict[str, List[Dict]]:
        """
        Get price history for all currencies

        Args:
            days (int): Number of days to retrieve

        Returns:
            dict: Dictionary with currency names as keys and history as values
        """
        cursor = self.connection.cursor()

        start_date = datetime.now() - timedelta(days=days)

        cursor.execute("""
            SELECT currency_name, chaos_value, change_24h,
                   profitability, timestamp
            FROM price_history
            WHERE timestamp >= ?
            ORDER BY currency_name, timestamp ASC
        """, (start_date.isoformat(),))

        rows = cursor.fetchall()

        # Organize by currency
        history = {}
        for row in rows:
            currency_name = row[0]
            if currency_name not in history:
                history[currency_name] = []

            history[currency_name].append({
                'chaos_value': row[1],
                'change_24h': row[2],
                'profitability': row[3],
                'timestamp': row[4]
            })

        return history

    def record_trade(self, currency_name: str, trade_type: str,
                     profit: float, notes: str = ""):
        """
        Record a trade for statistics

        Args:
            currency_name (str): Currency traded
            trade_type (str): Type of trade (BUY/SELL)
            profit (float): Profit made
            notes (str): Additional notes
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO trade_statistics
            (currency_name, trade_type, profit, trade_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            currency_name,
            trade_type,
            profit,
            datetime.now().isoformat(),
            notes
        ))

        self.connection.commit()
        logger.info(f"Recorded trade: {trade_type} {currency_name}")

    def get_statistics(self) -> Dict:
        """
        Get overall statistics

        Returns:
            dict: Statistics data
        """
        cursor = self.connection.cursor()

        # Total trades
        cursor.execute("SELECT COUNT(*) FROM trade_statistics")
        total_trades = cursor.fetchone()[0]

        # Most profitable currency
        cursor.execute("""
            SELECT currency_name, SUM(profit) as total_profit
            FROM trade_statistics
            GROUP BY currency_name
            ORDER BY total_profit DESC
            LIMIT 1
        """)
        most_profitable = cursor.fetchone()
        most_profitable_name = most_profitable[0] if most_profitable else "N/A"

        # Average profit
        cursor.execute("SELECT AVG(profit) FROM trade_statistics")
        avg_profit = cursor.fetchone()[0] or 0

        # Best trading time (hour of day with most profitable trades)
        cursor.execute("""
            SELECT strftime('%H', trade_date) as hour,
                   AVG(profit) as avg_profit
            FROM trade_statistics
            GROUP BY hour
            ORDER BY avg_profit DESC
            LIMIT 1
        """)
        best_time = cursor.fetchone()
        best_time_str = f"{best_time[0]}:00" if best_time else "N/A"

        return {
            'total_trades': total_trades,
            'most_profitable': most_profitable_name,
            'avg_profit': avg_profit,
            'best_time': best_time_str
        }

    def cleanup_old_data(self, days: int = None):
        """
        Remove old price history data

        Args:
            days (int): Keep data newer than this many days
        """
        if days is None:
            days = config.MAX_HISTORY_DAYS

        cursor = self.connection.cursor()

        cutoff_date = datetime.now() - timedelta(days=days)

        cursor.execute("""
            DELETE FROM price_history
            WHERE timestamp < ?
        """, (cutoff_date.isoformat(),))

        deleted = cursor.rowcount
        self.connection.commit()

        logger.info(f"Cleaned up {deleted} old price records")

    def get_latest_prices(self) -> Dict:
        """
        Get the most recent prices for all currencies

        Returns:
            dict: Latest prices
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT currency_name, chaos_value, change_24h,
                   profitability, timestamp
            FROM price_history
            WHERE id IN (
                SELECT MAX(id)
                FROM price_history
                GROUP BY currency_name
            )
        """)

        rows = cursor.fetchall()

        return {
            row[0]: {
                'chaosEquivalent': row[1],
                'change24h': row[2],
                'profitability': row[3],
                'timestamp': row[4]
            }
            for row in rows
        }

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
