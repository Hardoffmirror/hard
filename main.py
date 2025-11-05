#!/usr/bin/env python3
"""
PoE Currency Exchange Helper - Main Application
Overlay application for Path of Exile currency trading
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.overlay_window import OverlayWindow
from src.core.currency_tracker import CurrencyTracker
from src.database.db_manager import DatabaseManager

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Initialize database
    db_manager = DatabaseManager()

    # Initialize currency tracker
    currency_tracker = CurrencyTracker(db_manager)

    # Create and show overlay window
    overlay = OverlayWindow(currency_tracker, db_manager)
    overlay.show()

    # Start currency tracking
    currency_tracker.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
