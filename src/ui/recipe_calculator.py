"""
Recipe Calculator Widget
Calculate profitability of unique vendor recipes
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QPushButton, QGroupBox, QTableWidget,
                              QTableWidgetItem, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import logging
from src.data.unique_recipes import (get_all_recipes, get_recipe_categories,
                                      get_recipes_by_category, is_currency_item)
from src.api.poe_ninja_client import PoeNinjaClient

logger = logging.getLogger(__name__)


class RecipeCalculatorWidget(QWidget):
    """Widget for calculating vendor recipe profitability"""

    def __init__(self, currency_tracker):
        super().__init__()
        self.currency_tracker = currency_tracker
        self.poe_ninja_client = PoeNinjaClient()
        self.unique_prices = {}
        self.currency_prices = {}
        self.current_recipe = None

        self.init_ui()
        self.load_initial_data()

    def init_ui(self):
        """Initialize UI"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        scroll.setWidget(main_widget)

        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)
        outer_layout.addWidget(scroll)

        # Title
        title = QLabel("Калькулятор уникальных рецептов")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Recipe selection group
        selection_group = QGroupBox("Выбор рецепта")
        selection_group.setStyleSheet("""
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
        selection_layout = QVBoxLayout()
        selection_group.setLayout(selection_layout)

        # Category selector
        category_layout = QHBoxLayout()
        category_label = QLabel("Категория:")
        self.category_selector = QComboBox()
        self.category_selector.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                min-height: 25px;
            }
        """)
        self.category_selector.currentTextChanged.connect(self.on_category_changed)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_selector, 1)
        selection_layout.addLayout(category_layout)

        # Recipe selector
        recipe_layout = QHBoxLayout()
        recipe_label = QLabel("Рецепт:")
        self.recipe_selector = QComboBox()
        self.recipe_selector.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #FFD700;
                padding: 5px;
                min-height: 25px;
            }
        """)
        self.recipe_selector.currentTextChanged.connect(self.on_recipe_changed)
        recipe_layout.addWidget(recipe_label)
        recipe_layout.addWidget(self.recipe_selector, 1)
        selection_layout.addLayout(recipe_layout)

        # Refresh button
        refresh_btn = QPushButton("Обновить цены")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.refresh_prices)
        selection_layout.addWidget(refresh_btn)

        layout.addWidget(selection_group)

        # Recipe description
        self.description_label = QLabel("")
        self.description_label.setStyleSheet("font-size: 11px; color: #aaa; padding: 5px;")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        # Ingredients table
        ingredients_group = QGroupBox("Ингредиенты")
        ingredients_group.setStyleSheet("""
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
        ingredients_layout = QVBoxLayout()
        ingredients_group.setLayout(ingredients_layout)

        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels([
            "Предмет", "Количество", "Цена за шт.", "Сумма"
        ])
        self.ingredients_table.horizontalHeader().setStretchLastSection(True)
        self.ingredients_table.setStyleSheet("""
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
        ingredients_layout.addWidget(self.ingredients_table)

        layout.addWidget(ingredients_group)

        # Results group
        results_group = QGroupBox("Расчет прибыльности")
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

        self.total_cost_label = QLabel("Стоимость ингредиентов: -")
        self.total_cost_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.total_cost_label)

        self.result_price_label = QLabel("Цена результата: -")
        self.result_price_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.result_price_label)

        self.profit_label = QLabel("Прибыль: -")
        self.profit_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        results_layout.addWidget(self.profit_label)

        self.profit_percent_label = QLabel("Прибыль (%): -")
        self.profit_percent_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.profit_percent_label)

        self.recommendation_label = QLabel("Рекомендация: -")
        self.recommendation_label.setStyleSheet("font-size: 14px; padding: 5px;")
        results_layout.addWidget(self.recommendation_label)

        layout.addWidget(results_group)

        layout.addStretch()

    def load_initial_data(self):
        """Load initial data"""
        # Load categories
        categories = ['All'] + get_recipe_categories()
        self.category_selector.addItems(categories)

        # Load all recipes initially
        self.load_recipes('All')

    def load_recipes(self, category):
        """Load recipes for selected category"""
        self.recipe_selector.clear()

        if category == 'All':
            recipes = get_all_recipes()
        else:
            recipes = get_recipes_by_category(category)

        recipe_names = [r['name'] for r in recipes]
        self.recipe_selector.addItems(recipe_names)

    def on_category_changed(self, category):
        """Handle category change"""
        if category:
            self.load_recipes(category)

    def on_recipe_changed(self, recipe_name):
        """Handle recipe selection change"""
        if not recipe_name:
            return

        # Find recipe
        recipes = get_all_recipes()
        self.current_recipe = None

        for recipe in recipes:
            if recipe['name'] == recipe_name:
                self.current_recipe = recipe
                break

        if not self.current_recipe:
            return

        # Update description
        self.description_label.setText(self.current_recipe.get('description', ''))

        # Update ingredients table and calculate
        self.update_ingredients_table()
        self.calculate_profit()

    def refresh_prices(self):
        """Refresh prices from API"""
        try:
            # Get current league
            league = self.currency_tracker.current_league if hasattr(self.currency_tracker, 'current_league') else None

            # Fetch unique item prices
            self.unique_prices = self.poe_ninja_client.get_unique_items(league)

            # Fetch currency prices
            self.currency_prices = self.currency_tracker.get_current_rates()

            logger.info(f"Refreshed prices: {len(self.unique_prices)} uniques, {len(self.currency_prices)} currencies")

            # Recalculate if recipe selected
            if self.current_recipe:
                self.update_ingredients_table()
                self.calculate_profit()

        except Exception as e:
            logger.error(f"Failed to refresh prices: {e}")

    def update_ingredients_table(self):
        """Update ingredients table with current recipe"""
        if not self.current_recipe:
            return

        ingredients = self.current_recipe['ingredients']
        self.ingredients_table.setRowCount(len(ingredients))

        for i, ingredient in enumerate(ingredients):
            item_name = ingredient['item']
            quantity = ingredient['quantity']

            # Get price
            price = self.get_item_price(item_name)

            # Item name
            self.ingredients_table.setItem(i, 0, QTableWidgetItem(item_name))

            # Quantity
            self.ingredients_table.setItem(i, 1, QTableWidgetItem(str(quantity)))

            # Price per item
            price_item = QTableWidgetItem(f"{price:.2f}c" if price > 0 else "N/A")
            if price == 0:
                price_item.setForeground(QColor(255, 100, 100))
            self.ingredients_table.setItem(i, 2, price_item)

            # Total
            total = price * quantity
            total_item = QTableWidgetItem(f"{total:.2f}c" if total > 0 else "N/A")
            self.ingredients_table.setItem(i, 3, total_item)

    def get_item_price(self, item_name):
        """Get price for an item"""
        # Check if it's a currency
        if is_currency_item(item_name):
            # Look in currency prices
            if item_name in self.currency_prices:
                return self.currency_prices[item_name].get('chaosEquivalent', 0)

        # Check unique items
        if item_name in self.unique_prices:
            return self.unique_prices[item_name].get('chaosValue', 0)

        # Special handling for "Unique Ring" in Loreweave recipe
        if item_name == 'Unique Ring':
            # Average price for cheap unique rings (rough estimate)
            return 1.0

        return 0

    def calculate_profit(self):
        """Calculate profit from recipe"""
        if not self.current_recipe:
            self.clear_results()
            return

        # Calculate total cost
        total_cost = 0
        all_prices_available = True

        for ingredient in self.current_recipe['ingredients']:
            item_name = ingredient['item']
            quantity = ingredient['quantity']
            price = self.get_item_price(item_name)

            if price == 0:
                all_prices_available = False

            total_cost += price * quantity

        # Get result price
        result_name = self.current_recipe['result']
        result_price = self.get_item_price(result_name)

        # Calculate profit
        profit = result_price - total_cost
        profit_percent = (profit / total_cost * 100) if total_cost > 0 else 0

        # Update labels
        cost_color = "#FFFFFF" if all_prices_available else "#FF6666"
        self.total_cost_label.setText(f"Стоимость ингредиентов: {total_cost:.2f} chaos")
        self.total_cost_label.setStyleSheet(f"font-size: 14px; padding: 5px; color: {cost_color};")

        result_color = "#FFFFFF" if result_price > 0 else "#FF6666"
        self.result_price_label.setText(f"Цена результата: {result_price:.2f} chaos")
        self.result_price_label.setStyleSheet(f"font-size: 14px; padding: 5px; color: {result_color};")

        # Profit with color
        profit_color = "#00FF00" if profit > 0 else "#FF0000" if profit < 0 else "#FFFFFF"
        self.profit_label.setText(f"Прибыль: {profit:+.2f} chaos")
        self.profit_label.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 5px; color: {profit_color};")

        self.profit_percent_label.setText(f"Прибыль (%): {profit_percent:+.2f}%")
        self.profit_percent_label.setStyleSheet(f"font-size: 14px; padding: 5px; color: {profit_color};")

        # Recommendation
        if not all_prices_available or result_price == 0:
            recommendation = "⚠ Недостаточно данных о ценах"
            rec_color = "#FFA500"
        elif profit_percent >= 20:
            recommendation = "✅ ОТЛИЧНО! Очень выгодный рецепт"
            rec_color = "#00FF00"
        elif profit_percent >= 10:
            recommendation = "✅ ХОРОШО! Выгодный рецепт"
            rec_color = "#90EE90"
        elif profit_percent > 0:
            recommendation = "⚠ ПРИЕМЛЕМО. Небольшая прибыль"
            rec_color = "#FFD700"
        else:
            recommendation = "❌ УБЫТОК! Не рекомендуется"
            rec_color = "#FF0000"

        self.recommendation_label.setText(f"Рекомендация: {recommendation}")
        self.recommendation_label.setStyleSheet(
            f"font-size: 14px; padding: 5px; font-weight: bold; color: {rec_color};"
        )

    def clear_results(self):
        """Clear result labels"""
        self.total_cost_label.setText("Стоимость ингредиентов: -")
        self.result_price_label.setText("Цена результата: -")
        self.profit_label.setText("Прибыль: -")
        self.profit_percent_label.setText("Прибыль (%): -")
        self.recommendation_label.setText("Рекомендация: -")
