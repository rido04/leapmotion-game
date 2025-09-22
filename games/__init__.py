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
        'name': 'Memory Game',
        'module': 'games.memory_game',
        'class': 'MemoryGame', 
        'description': 'Match pairs of cards to win',
        'preview_color': (128, 64, 255)  # PURPLE
    },
    {
        'name': 'Stack Tower',
        'module': 'games.stack_tower',
        'class': 'StackTowerGame',
        'description': 'Stack blocks to build the tallest tower',
        'preview_color': (255, 165, 0)  # Orange
    },
    {
        'name': 'Balloon Pop',
        'module': 'games.balloon_pop',
        'class': 'BalloonPopGame',
        'description': 'Pop balloons while avoiding bombs',
        'preview_color': (255, 192, 203)  # Pink
    }
]