"""
Resale Calculator Widget
Calculate profit from currency resale
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QLineEdit, QPushButton, QGroupBox,
                              QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
import logging

logger = logging.getLogger(__name__)


class ResaleCalculatorWidget(QWidget):
    """Widget for calculating currency resale profit"""

    def __init__(self, currency_tracker):
        super().__init__()
        self.currency_tracker = currency_tracker
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("Калькулятор перепродажи валюты")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Input group
        input_group = QGroupBox("Параметры сделки")
        input_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #FFD700;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        input_layout = QFormLayout()
        input_group.setLayout(input_layout)

        # Currency selector
        self.currency_selector = QComboBox()
        self.currency_selector.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                min-height: 25px;
            }
        """)
        input_layout.addRow("Валюта:", self.currency_selector)

        # Quantity input
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, 999999))
        self.quantity_input.setText("1")
        self.quantity_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                min-height: 25px;
            }
        """)
        self.quantity_input.textChanged.connect(self.calculate_profit)
        input_layout.addRow("Количество:", self.quantity_input)

        # Buy price input
        self.buy_price_input = QLineEdit()
        self.buy_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.buy_price_input.setPlaceholderText("Цена покупки в chaos")
        self.buy_price_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                min-height: 25px;
            }
        """)
        self.buy_price_input.textChanged.connect(self.calculate_profit)
        input_layout.addRow("Цена покупки (chaos):", self.buy_price_input)

        # Sell price input
        self.sell_price_input = QLineEdit()
        self.sell_price_input.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.sell_price_input.setPlaceholderText("Цена продажи в chaos")
        self.sell_price_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                min-height: 25px;
            }
        """)
        self.sell_price_input.textChanged.connect(self.calculate_profit)
        input_layout.addRow("Цена продажи (chaos):", self.sell_price_input)

        layout.addWidget(input_group)

        # Quick fill button
        quick_fill_layout = QHBoxLayout()
        quick_fill_btn = QPushButton("Заполнить текущими ценами")
        quick_fill_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #FFD700;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        quick_fill_btn.clicked.connect(self.fill_current_prices)
        quick_fill_layout.addStretch()
        quick_fill_layout.addWidget(quick_fill_btn)
        quick_fill_layout.addStretch()
        layout.addLayout(quick_fill_layout)

        # Results group
        results_group = QGroupBox("Результаты")
        results_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #FFD700;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)

        # Result labels
        self.total_buy_label = QLabel("Стоимость покупки: -")
        self.total_buy_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.total_buy_label)

        self.total_sell_label = QLabel("Стоимость продажи: -")
        self.total_sell_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.total_sell_label)

        self.profit_chaos_label = QLabel("Прибыль (chaos): -")
        self.profit_chaos_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.profit_chaos_label)

        self.profit_percent_label = QLabel("Прибыль (%): -")
        self.profit_percent_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        results_layout.addWidget(self.profit_percent_label)

        self.recommendation_label = QLabel("Рекомендация: -")
        self.recommendation_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.recommendation_label)

        layout.addWidget(results_group)

        # Market info
        self.market_info_label = QLabel("")
        self.market_info_label.setStyleSheet("font-size: 11px; color: #aaa; padding: 10px;")
        self.market_info_label.setWordWrap(True)
        layout.addWidget(self.market_info_label)

        layout.addStretch()

        # Load currencies
        self.load_currencies()

        # Connect currency change
        self.currency_selector.currentTextChanged.connect(self.on_currency_changed)

    def load_currencies(self):
        """Load available currencies"""
        rates = self.currency_tracker.get_current_rates()
        self.currency_selector.clear()
        if rates:
            self.currency_selector.addItems(sorted(rates.keys()))
        else:
            self.currency_selector.addItem("No data")

    def fill_current_prices(self):
        """Fill buy/sell prices with current market prices"""
        currency = self.currency_selector.currentText()
        if not currency:
            return

        rates = self.currency_tracker.get_current_rates()
        if currency not in rates:
            return

        data = rates[currency]
        chaos_value = data.get('chaosEquivalent', 0)

        # Set conservative buy/sell spread
        if chaos_value > 0:
            # Buy 2% above market, sell 2% below for realistic flip
            buy_price = chaos_value * 1.02
            sell_price = chaos_value * 0.98

            self.buy_price_input.setText(f"{buy_price:.2f}")
            self.sell_price_input.setText(f"{sell_price:.2f}")

            # Show market info
            change_24h = data.get('change24h', 0)
            self.market_info_label.setText(
                f"Текущая рыночная цена: {chaos_value:.2f} chaos\n"
                f"Изменение за 24ч: {change_24h:+.2f}%"
            )

    def on_currency_changed(self, currency):
        """Handle currency selection change"""
        if not currency:
            return

        rates = self.currency_tracker.get_current_rates()
        if currency not in rates:
            self.market_info_label.setText("Нет данных для этой валюты")
            return

        data = rates[currency]
        chaos_value = data.get('chaosEquivalent', 0)
        change_24h = data.get('change24h', 0)
        profitability = data.get('profitability', 0)

        self.market_info_label.setText(
            f"Рыночная цена: {chaos_value:.2f} chaos | "
            f"Изменение 24ч: {change_24h:+.2f}% | "
            f"Прибыльность: {profitability:.2f}%"
        )

    def calculate_profit(self):
        """Calculate profit from resale"""
        try:
            quantity = int(self.quantity_input.text()) if self.quantity_input.text() else 0
            buy_price = float(self.buy_price_input.text()) if self.buy_price_input.text() else 0
            sell_price = float(self.sell_price_input.text()) if self.sell_price_input.text() else 0

            if quantity <= 0 or buy_price <= 0 or sell_price <= 0:
                self.clear_results()
                return

            # Calculate totals
            total_buy = buy_price * quantity
            total_sell = sell_price * quantity
            profit_chaos = total_sell - total_buy
            profit_percent = (profit_chaos / total_buy) * 100 if total_buy > 0 else 0

            # Update labels
            self.total_buy_label.setText(f"Стоимость покупки: {total_buy:.2f} chaos")
            self.total_sell_label.setText(f"Стоимость продажи: {total_sell:.2f} chaos")

            # Profit with color
            profit_color = "#00FF00" if profit_chaos > 0 else "#FF0000" if profit_chaos < 0 else "#FFFFFF"
            self.profit_chaos_label.setText(f"Прибыль (chaos): {profit_chaos:+.2f} chaos")
            self.profit_chaos_label.setStyleSheet(f"font-size: 14px; padding: 5px; color: {profit_color};")

            self.profit_percent_label.setText(f"Прибыль (%): {profit_percent:+.2f}%")
            self.profit_percent_label.setStyleSheet(
                f"font-size: 16px; font-weight: bold; padding: 5px; color: {profit_color};"
            )

            # Recommendation
            if profit_percent >= 10:
                recommendation = "ОТЛИЧНО! Очень выгодная сделка"
                rec_color = "#00FF00"
            elif profit_percent >= 5:
                recommendation = "ХОРОШО! Выгодная сделка"
                rec_color = "#90EE90"
            elif profit_percent > 0:
                recommendation = "ПРИЕМЛЕМО. Небольшая прибыль"
                rec_color = "#FFD700"
            elif profit_percent == 0:
                recommendation = "БЕЗ ПРИБЫЛИ"
                rec_color = "#AAAAAA"
            else:
                recommendation = "УБЫТОК! Не рекомендуется"
                rec_color = "#FF0000"

            self.recommendation_label.setText(f"Рекомендация: {recommendation}")
            self.recommendation_label.setStyleSheet(
                f"font-size: 14px; padding: 5px; font-weight: bold; color: {rec_color};"
            )

        except ValueError:
            self.clear_results()

    def clear_results(self):
        """Clear result labels"""
        self.total_buy_label.setText("Стоимость покупки: -")
        self.total_sell_label.setText("Стоимость продажи: -")
        self.profit_chaos_label.setText("Прибыль (chaos): -")
        self.profit_chaos_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.profit_percent_label.setText("Прибыль (%): -")
        self.profit_percent_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        self.recommendation_label.setText("Рекомендация: -")
        self.recommendation_label.setStyleSheet("font-size: 14px; padding: 5px;")
