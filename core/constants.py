# core/constants.py
"""
Shared constants for all games
"""

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Grid settings (for tic tac toe)
GRID_SIZE = 450
CELL_SIZE = GRID_SIZE // 3
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_SIZE) // 2
GRID_OFFSET_Y = 180

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
DARK_GRAY = (40, 40, 50)
LIGHT_GRAY = (100, 100, 120)
BLUE = (64, 128, 255)
BLUE_DARK = (32, 64, 200)
RED = (255, 64, 64)
RED_DARK = (200, 32, 32)
GREEN = (64, 255, 128)
GREEN_DARK = (32, 200, 64)
YELLOW = (255, 220, 64)
PURPLE = (128, 64, 255)
CYAN = (64, 255, 255)

# Font sizes
FONT_TITLE = 64
FONT_LARGE = 120
FONT_MEDIUM = 32
FONT_SMALL = 24

# Hand tracking settings
HAND_PINCH_THRESHOLD = 30
HAND_HOVER_TIME_THRESHOLD = 1.0  # seconds
HAND_TRACKING_UPDATE_RATE = 0.01  # seconds