# main.py
"""
Entry point for Hand Tracking Games Collection
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_menu import MainMenu

if __name__ == "__main__":
    try:
        menu = MainMenu()
        menu.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)