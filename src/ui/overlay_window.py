"""
Overlay Window - Main application window
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QTabWidget, QScrollArea,
                              QTableWidget, QTableWidgetItem, QComboBox, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from src.ui.resale_calculator import ResaleCalculatorWidget
from src.ui.recipe_calculator import RecipeCalculatorWidget
import config
import logging

logger = logging.getLogger(__name__)


class OverlayWindow(QMainWindow):
    """Main application window"""

    def __init__(self, currency_tracker, db_manager):
        super().__init__()
        self.currency_tracker = currency_tracker
        self.db_manager = db_manager
        self.current_league = config.CURRENT_LEAGUE
        self.show_all_currencies = False

        self.init_ui()
        self.load_available_leagues()
        self.setup_update_timer()

    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("PoE Currency Exchange Helper")
        self.setGeometry(100, 100, 1000, 700)  # Bigger default size
        self.setMinimumSize(800, 600)  # Minimum size

        # Modern window (resizable)
        self.setWindowFlags(Qt.Window)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial;
                font-size: 11px;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #45475a;
                border: 1px solid #585b70;
            }
            QPushButton:pressed {
                background-color: #585b70;
            }
            QTabWidget::pane {
                border: 1px solid #45475a;
                background-color: #1e1e2e;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #cdd6f4;
                padding: 10px 20px;
                border: 1px solid #45475a;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #45475a;
            }
            QTableWidget {
                background-color: #181825;
                alternate-background-color: #1e1e2e;
                color: #cdd6f4;
                gridline-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 8px;
                font-weight: bold;
            }
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 6px 12px;
                border-radius: 6px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #89b4fa;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cdd6f4;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
                selection-color: #1e1e2e;
                border: 1px solid #45475a;
            }
            QCheckBox {
                color: #cdd6f4;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #45475a;
                border-radius: 4px;
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
            QCheckBox::indicator:hover {
                border-color: #89b4fa;
            }
            QScrollBar:vertical {
                background-color: #1e1e2e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #45475a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #585b70;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Top bar with settings
        top_bar = self.create_top_bar()
        layout.addLayout(top_bar)

        # Tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_exchange_tab()
        self.create_calculator_tab()
        self.create_recipe_tab()
        self.create_statistics_tab()

    def create_top_bar(self):
        """Create top bar with league selector and settings"""
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        # Title
        title_label = QLabel("💰 PoE Currency Helper")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #89b4fa;
            padding: 5px;
        """)
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # Show all currencies checkbox
        self.show_all_checkbox = QCheckBox("Показать все валюты")
        self.show_all_checkbox.setChecked(False)
        self.show_all_checkbox.stateChanged.connect(self.on_show_all_changed)
        top_layout.addWidget(self.show_all_checkbox)

        # League selector
        league_label = QLabel("Лига:")
        league_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(league_label)

        self.league_selector = QComboBox()
        self.league_selector.currentTextChanged.connect(self.on_league_changed)
        top_layout.addWidget(self.league_selector)

        # Refresh button
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_all_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        top_layout.addWidget(refresh_btn)

        return top_layout

    def create_exchange_tab(self):
        """Create the exchange rates tab"""
        exchange_widget = QWidget()
        layout = QVBoxLayout()
        exchange_widget.setLayout(layout)
        layout.setSpacing(10)

        # Info label
        info_label = QLabel("💱 Текущие курсы валют")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #89b4fa; padding: 5px;")
        layout.addWidget(info_label)

        # Table for exchange rates
        self.exchange_table = QTableWidget()
        self.exchange_table.setColumnCount(5)
        self.exchange_table.setHorizontalHeaderLabels([
            "Валюта", "Цена (Chaos)", "Изменение 24ч", "Профит %", "Рекомендация"
        ])
        self.exchange_table.setAlternatingRowColors(True)
        self.exchange_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exchange_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exchange_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.exchange_table.setColumnWidth(0, 200)
        self.exchange_table.setColumnWidth(1, 120)
        self.exchange_table.setColumnWidth(2, 120)
        self.exchange_table.setColumnWidth(3, 100)

        layout.addWidget(self.exchange_table)

        self.tabs.addTab(exchange_widget, "💱 Курсы")

    def create_calculator_tab(self):
        """Create the resale calculator tab"""
        calculator_widget = ResaleCalculatorWidget(self.currency_tracker)
        self.tabs.addTab(calculator_widget, "🧮 Калькулятор")

    def create_recipe_tab(self):
        """Create the recipe calculator tab"""
        recipe_widget = RecipeCalculatorWidget(self.currency_tracker)
        self.tabs.addTab(recipe_widget, "📜 Рецепты")

    def create_statistics_tab(self):
        """Create the statistics tab"""
        stats_widget = QWidget()
        layout = QVBoxLayout()
        stats_widget.setLayout(layout)
        layout.setSpacing(15)

        # Title
        title = QLabel("📊 Статистика торговли")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Statistics cards
        self.stats_labels = {}

        stats_info = [
            ("Всего сделок:", "total_trades", "📈"),
            ("Самая прибыльная валюта:", "most_profitable", "💎"),
            ("Средняя прибыль:", "avg_profit", "💰"),
            ("Лучшее время для торговли:", "best_time", "⏰")
        ]

        for label_text, key, icon in stats_info:
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background-color: #313244;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            card_layout = QHBoxLayout()
            card.setLayout(card_layout)

            # Icon and label
            left_layout = QVBoxLayout()
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; font-size: 12px;")
            left_layout.addWidget(icon_label)
            left_layout.addWidget(label)
            card_layout.addLayout(left_layout)

            card_layout.addStretch()

            # Value
            value = QLabel("Загрузка...")
            value.setStyleSheet("color: #89b4fa; font-size: 18px; font-weight: bold;")
            self.stats_labels[key] = value
            card_layout.addWidget(value)

            layout.addWidget(card)

        layout.addStretch()

        self.tabs.addTab(stats_widget, "📊 Статистика")

    def setup_update_timer(self):
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(config.UPDATE_INTERVAL * 1000)

    def update_data(self):
        """Update all data displays"""
        self.update_exchange_rates()
        self.update_statistics()

    def refresh_all_data(self):
        """Manually refresh all data"""
        self.currency_tracker.fetch_prices()
        self.update_data()

    def on_show_all_changed(self, state):
        """Handle show all currencies checkbox"""
        self.show_all_currencies = state == Qt.Checked
        self.update_exchange_rates()

    def get_major_currencies(self):
        """Get list of major currencies to show by default"""
        return [
            'Divine Orb',
            'Exalted Orb',
            'Chaos Orb',
            'Mirror of Kalandra',
            'Orb of Alchemy',
            'Orb of Alteration',
            'Orb of Fusing',
            'Chromatic Orb',
            "Jeweller's Orb",
            'Vaal Orb',
            'Regal Orb',
            'Orb of Scouring',
            'Blessed Orb',
            "Gemcutter's Prism",
            "Cartographer's Chisel",
            'Orb of Regret',
            'Orb of Annulment',
            'Ancient Orb',
            'Harbinger\'s Orb',
        ]

    def update_exchange_rates(self):
        """Update the exchange rates table"""
        rates = self.currency_tracker.get_current_rates()

        # Filter currencies if needed
        if not self.show_all_currencies:
            major_currencies = self.get_major_currencies()
            filtered_rates = {k: v for k, v in rates.items() if k in major_currencies}
        else:
            filtered_rates = rates

        self.exchange_table.setRowCount(len(filtered_rates))

        for i, (currency, data) in enumerate(sorted(filtered_rates.items())):
            # Currency name
            name_item = QTableWidgetItem(currency)
            name_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.exchange_table.setItem(i, 0, name_item)

            # Chaos value
            chaos_value = data.get('chaosEquivalent', 0)
            chaos_item = QTableWidgetItem(f"{chaos_value:.2f}")
            chaos_item.setTextAlignment(Qt.AlignCenter)
            self.exchange_table.setItem(i, 1, chaos_item)

            # 24h change
            change = data.get('change24h', 0)
            change_item = QTableWidgetItem(f"{change:+.2f}%")
            change_item.setTextAlignment(Qt.AlignCenter)
            if change > 0:
                change_item.setForeground(QColor(166, 227, 161))  # Green
            elif change < 0:
                change_item.setForeground(QColor(243, 139, 168))  # Red
            self.exchange_table.setItem(i, 2, change_item)

            # Profit percentage
            profit = data.get('profitability', 0)
            profit_item = QTableWidgetItem(f"{profit:.2f}%")
            profit_item.setTextAlignment(Qt.AlignCenter)
            if profit >= config.MIN_PROFIT_PERCENTAGE:
                profit_item.setForeground(QColor(166, 227, 161))
            self.exchange_table.setItem(i, 3, profit_item)

            # Recommendation
            recommendation = "✅ BUY" if profit >= config.MIN_PROFIT_PERCENTAGE else "⏸ HOLD"
            rec_item = QTableWidgetItem(recommendation)
            rec_item.setTextAlignment(Qt.AlignCenter)
            if recommendation == "✅ BUY":
                rec_item.setForeground(QColor(166, 227, 161))
            self.exchange_table.setItem(i, 4, rec_item)

    def update_statistics(self):
        """Update statistics display"""
        stats = self.db_manager.get_statistics()

        self.stats_labels['total_trades'].setText(str(stats.get('total_trades', 0)))
        self.stats_labels['most_profitable'].setText(stats.get('most_profitable', 'N/A'))
        self.stats_labels['avg_profit'].setText(f"{stats.get('avg_profit', 0):.2f}%")
        self.stats_labels['best_time'].setText(stats.get('best_time', 'N/A'))

    def load_available_leagues(self):
        """Load available leagues from API"""
        try:
            from src.api.poe_ninja_client import PoeNinjaClient
            client = PoeNinjaClient()
            leagues = client.get_available_leagues()

            self.league_selector.clear()
            self.league_selector.addItems(leagues)

            # Set current league
            if self.current_league in leagues:
                self.league_selector.setCurrentText(self.current_league)
            elif leagues:
                self.current_league = leagues[0]
                self.league_selector.setCurrentText(self.current_league)

            logger.info(f"Loaded {len(leagues)} leagues")

        except Exception as e:
            logger.error(f"Failed to load leagues: {e}")
            self.league_selector.addItem(self.current_league)

    def on_league_changed(self, league):
        """Handle league selection change"""
        if not league or league == self.current_league:
            return

        logger.info(f"League changed: {self.current_league} -> {league}")
        self.current_league = league
        config.CURRENT_LEAGUE = league
        self.currency_tracker.current_league = league

        # Refresh data for new league
        self.refresh_all_data()
