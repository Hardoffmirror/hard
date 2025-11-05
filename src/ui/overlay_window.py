"""
Overlay Window - Transparent window that displays on top of the game
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QTabWidget, QScrollArea,
                              QTableWidget, QTableWidgetItem, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette
from src.ui.resale_calculator import ResaleCalculatorWidget
from src.ui.recipe_calculator import RecipeCalculatorWidget
import config
import logging

logger = logging.getLogger(__name__)


class OverlayWindow(QMainWindow):
    """Main overlay window that appears on top of the game"""

    def __init__(self, currency_tracker, db_manager):
        super().__init__()
        self.currency_tracker = currency_tracker
        self.db_manager = db_manager
        self.dragging = False
        self.offset = QPoint()
        self.current_league = config.CURRENT_LEAGUE

        self.init_ui()
        self.load_available_leagues()
        self.setup_update_timer()

    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("PoE Currency Exchange Helper")
        self.setGeometry(
            config.OVERLAY_X,
            config.OVERLAY_Y,
            config.OVERLAY_WIDTH,
            config.OVERLAY_HEIGHT
        )

        # Make window frameless and always on top
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # Set window opacity
        self.setWindowOpacity(config.OVERLAY_OPACITY)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set background color and style
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(30, 30, 30, 230);
                border: 2px solid #FFD700;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QTabWidget::pane {
                border: 1px solid #FFD700;
                background-color: rgba(40, 40, 40, 200);
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: white;
                padding: 5px 10px;
                border: 1px solid #FFD700;
            }
            QTabBar::tab:selected {
                background-color: #FFD700;
                color: black;
            }
            QTableWidget {
                background-color: rgba(40, 40, 40, 200);
                color: white;
                gridline-color: #FFD700;
            }
            QHeaderView::section {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Title bar with drag and close button
        title_bar = self.create_title_bar()
        layout.addLayout(title_bar)

        # Tab widget for different views
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_exchange_tab()
        self.create_calculator_tab()
        self.create_recipe_tab()
        self.create_history_tab()
        self.create_statistics_tab()

    def create_title_bar(self):
        """Create custom title bar with drag functionality"""
        title_layout = QHBoxLayout()

        # Title label
        title_label = QLabel("PoE Currency Helper")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFD700;")
        title_layout.addWidget(title_label)

        # League selector
        league_label = QLabel("League:")
        league_label.setStyleSheet("font-size: 11px; margin-left: 10px;")
        title_layout.addWidget(league_label)

        self.league_selector = QComboBox()
        self.league_selector.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 3px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFD700;
            }
        """)
        self.league_selector.currentTextChanged.connect(self.on_league_changed)
        title_layout.addWidget(self.league_selector)

        title_layout.addStretch()

        # Minimize button
        minimize_btn = QPushButton("_")
        minimize_btn.setMaximumWidth(30)
        minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_btn)

        # Close button
        close_btn = QPushButton("X")
        close_btn.setMaximumWidth(30)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        return title_layout

    def create_exchange_tab(self):
        """Create the exchange rates tab"""
        exchange_widget = QWidget()
        layout = QVBoxLayout()
        exchange_widget.setLayout(layout)

        # Table for exchange rates
        self.exchange_table = QTableWidget()
        self.exchange_table.setColumnCount(5)
        self.exchange_table.setHorizontalHeaderLabels([
            "Currency", "Chaos Value", "Change 24h", "Profit %", "Recommendation"
        ])
        self.exchange_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.exchange_table)

        # Refresh button
        refresh_btn = QPushButton("Refresh Prices")
        refresh_btn.clicked.connect(self.refresh_exchange_rates)
        layout.addWidget(refresh_btn)

        self.tabs.addTab(exchange_widget, "Exchange Rates")

    def create_calculator_tab(self):
        """Create the resale calculator tab"""
        calculator_widget = ResaleCalculatorWidget(self.currency_tracker)
        self.tabs.addTab(calculator_widget, "Calculator")

    def create_recipe_tab(self):
        """Create the recipe calculator tab"""
        recipe_widget = RecipeCalculatorWidget(self.currency_tracker)
        self.tabs.addTab(recipe_widget, "Recipes")

    def create_history_tab(self):
        """Create the price history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout()
        history_widget.setLayout(layout)

        # Price history chart placeholder
        chart_label = QLabel("Price History Chart")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("font-size: 16px; padding: 50px;")
        layout.addWidget(chart_label)

        # Note about charts
        note_label = QLabel("Charts will be implemented with matplotlib integration")
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(note_label)

        self.tabs.addTab(history_widget, "Price History")

    def create_statistics_tab(self):
        """Create the statistics tab"""
        stats_widget = QWidget()
        layout = QVBoxLayout()
        stats_widget.setLayout(layout)

        # Statistics labels
        self.stats_labels = {}

        stats_info = [
            ("Total Trades Tracked:", "total_trades"),
            ("Most Profitable Currency:", "most_profitable"),
            ("Average Daily Profit:", "avg_profit"),
            ("Best Trading Time:", "best_time")
        ]

        for label_text, key in stats_info:
            h_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            value = QLabel("Loading...")
            value.setStyleSheet("color: #FFD700;")
            self.stats_labels[key] = value

            h_layout.addWidget(label)
            h_layout.addStretch()
            h_layout.addWidget(value)
            layout.addLayout(h_layout)

        layout.addStretch()

        self.tabs.addTab(stats_widget, "Statistics")

    def setup_update_timer(self):
        """Setup timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(config.UPDATE_INTERVAL * 1000)  # Convert to milliseconds

    def update_data(self):
        """Update all data displays"""
        self.update_exchange_rates()
        self.update_statistics()

    def refresh_exchange_rates(self):
        """Manually refresh exchange rates"""
        self.currency_tracker.fetch_prices()
        self.update_exchange_rates()

    def update_exchange_rates(self):
        """Update the exchange rates table"""
        rates = self.currency_tracker.get_current_rates()
        self.exchange_table.setRowCount(len(rates))

        for i, (currency, data) in enumerate(rates.items()):
            # Currency name
            self.exchange_table.setItem(i, 0, QTableWidgetItem(currency))

            # Chaos value
            chaos_value = data.get('chaosEquivalent', 0)
            self.exchange_table.setItem(i, 1, QTableWidgetItem(f"{chaos_value:.2f}"))

            # 24h change
            change = data.get('change24h', 0)
            change_item = QTableWidgetItem(f"{change:+.2f}%")
            if change > 0:
                change_item.setForeground(QColor(0, 255, 0))
            elif change < 0:
                change_item.setForeground(QColor(255, 0, 0))
            self.exchange_table.setItem(i, 2, change_item)

            # Profit percentage
            profit = data.get('profitability', 0)
            profit_item = QTableWidgetItem(f"{profit:.2f}%")
            if profit >= config.MIN_PROFIT_PERCENTAGE:
                profit_item.setForeground(QColor(0, 255, 0))
            self.exchange_table.setItem(i, 3, profit_item)

            # Recommendation
            recommendation = "BUY" if profit >= config.MIN_PROFIT_PERCENTAGE else "HOLD"
            rec_item = QTableWidgetItem(recommendation)
            if recommendation == "BUY":
                rec_item.setForeground(QColor(0, 255, 0))
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
            # Add default league
            self.league_selector.addItem(self.current_league)

    def on_league_changed(self, league):
        """Handle league selection change"""
        if not league or league == self.current_league:
            return

        logger.info(f"League changed: {self.current_league} -> {league}")
        self.current_league = league

        # Update config
        config.CURRENT_LEAGUE = league

        # Refresh data for new league
        self.currency_tracker.fetch_prices()
        self.update_data()

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
