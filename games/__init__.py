# games/__init__.py
"""
Games package - contains all available games
"""

from .base_game import BaseGame

__all__ = ['BaseGame']

# Game registry - add new games here
AVAILABLE_GAMES = [
    {
        'name': 'Tic Tac Toe',
        'module': 'games.tic_tac_toe', 
        'class': 'TicTacToeGame',
        'description': 'Classic strategy game with hand tracking',
        'preview_color': (64, 255, 255)  # CYAN
    },
    {
        'name': 'Fruit Slash',
        'module': 'games.fruit_ninja_game',
        'class': 'FruitNinjaGame',
        'description': 'Swipe to slice fruits with hand gestures',
        'preview_color': (255, 165, 0)  # Orange
    },
    {
        'name': 'Memory Game',
        'module': 'games.memory_game',
        'class': 'MemoryGame', 
        'description': 'Match pairs of cards to win',
        'preview_color': (128, 64, 255)  # PURPLE
    },
    {
        'name': 'Balloon Pop',
        'module': 'games.balloon_pop',
        'class': 'BalloonPopGame',
        'description': 'Pop balloons before they float away',
        'preview_color': (255, 192, 203)  # Pink
    }
]