"""
Chart Widget
Widget for displaying price charts in the overlay
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from src.utils.chart_generator import ChartGenerator
import logging

logger = logging.getLogger(__name__)


class ChartWidget(QWidget):
    """Widget for displaying charts"""

    def __init__(self, db_manager, currency_tracker):
        super().__init__()
        self.db_manager = db_manager
        self.currency_tracker = currency_tracker
        self.chart_generator = ChartGenerator()

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Control panel
        control_layout = QHBoxLayout()

        # Currency selector
        self.currency_selector = QComboBox()
        self.currency_selector.currentTextChanged.connect(self.on_currency_changed)
        control_layout.addWidget(QLabel("Currency:"))
        control_layout.addWidget(self.currency_selector)

        # Chart type selector
        self.chart_type_selector = QComboBox()
        self.chart_type_selector.addItems([
            "Price History",
            "Profitability",
            "Trend Comparison",
            "Volatility"
        ])
        self.chart_type_selector.currentTextChanged.connect(self.update_chart)
        control_layout.addWidget(QLabel("Chart:"))
        control_layout.addWidget(self.chart_type_selector)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_chart)
        control_layout.addWidget(refresh_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Chart display
        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setMinimumSize(600, 400)
        self.chart_label.setStyleSheet("border: 1px solid #FFD700;")
        layout.addWidget(self.chart_label)

        # Load currencies
        self.load_currencies()

        # Show initial chart
        self.update_chart()

    def load_currencies(self):
        """Load available currencies"""
        rates = self.currency_tracker.get_current_rates()
        self.currency_selector.clear()
        self.currency_selector.addItems(sorted(rates.keys()))

    def on_currency_changed(self, currency):
        """Handle currency selection change"""
        if self.chart_type_selector.currentText() == "Price History":
            self.update_chart()

    def update_chart(self):
        """Update the displayed chart"""
        try:
            chart_type = self.chart_type_selector.currentText()

            if chart_type == "Price History":
                self.show_price_history()
            elif chart_type == "Profitability":
                self.show_profitability()
            elif chart_type == "Trend Comparison":
                self.show_trend_comparison()
            elif chart_type == "Volatility":
                self.show_volatility()

        except Exception as e:
            logger.error(f"Failed to update chart: {e}")
            self.show_error("Failed to generate chart")

    def show_price_history(self):
        """Show price history chart"""
        currency = self.currency_selector.currentText()
        if not currency:
            return

        history = self.db_manager.get_price_history(currency, days=7)

        chart_data = self.chart_generator.create_price_history_chart(
            history, currency
        )

        self.display_chart(chart_data)

    def show_profitability(self):
        """Show profitability comparison chart"""
        rates = self.currency_tracker.get_current_rates()

        chart_data = self.chart_generator.create_profitability_chart(rates)

        self.display_chart(chart_data)

    def show_trend_comparison(self):
        """Show trend comparison chart"""
        history = self.db_manager.get_all_currencies_history(days=7)

        chart_data = self.chart_generator.create_trend_chart(history)

        self.display_chart(chart_data)

    def show_volatility(self):
        """Show volatility chart"""
        rates = self.currency_tracker.get_current_rates()

        chart_data = self.chart_generator.create_volatility_chart(rates)

        self.display_chart(chart_data)

    def display_chart(self, chart_data: bytes):
        """
        Display chart from bytes

        Args:
            chart_data (bytes): PNG image data
        """
        try:
            # Convert bytes to QPixmap
            image = QImage()
            image.loadFromData(chart_data)

            pixmap = QPixmap.fromImage(image)

            # Scale to fit
            scaled_pixmap = pixmap.scaled(
                self.chart_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.chart_label.setPixmap(scaled_pixmap)

        except Exception as e:
            logger.error(f"Failed to display chart: {e}")
            self.show_error("Failed to display chart")

    def show_error(self, message: str):
        """
        Show error message

        Args:
            message (str): Error message
        """
        self.chart_label.setText(message)
        self.chart_label.setStyleSheet("color: red; font-size: 14px;")
