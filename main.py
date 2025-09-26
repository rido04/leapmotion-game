# main.py (new version)
import sys
import os
import configparser
from pathlib import Path

def load_game_config():
    """Load game configuration from installer"""
    config_file = Path("game_config.ini")
    
    if not config_file.exists():
        print("Configuration file not found!")
        return None
        
    config = configparser.ConfigParser()
    config.read(config_file)
    
    try:
        # Baca semua section yang diperlukan
        game_config = {
            'selected_game': config['GAME']['selected_game'],
            'fullscreen': config.getboolean('DISPLAY', 'fullscreen', fallback=True),
            'kiosk_mode': config.getboolean('DISPLAY', 'kiosk_mode', fallback=False)
        }
        return game_config
    except KeyError as e:
        print(f"Invalid configuration file: {e}")
        return None

def launch_selected_game(game_config):
    """Launch the selected game directly"""
    try:
        game_name = game_config['selected_game']
        if game_name == 'tic_tac_toe':
            from games.tic_tac_toe import TicTacToeGame
            game = TicTacToeGame(game_config)
            
        elif game_name == 'memory_game':
            from games.memory_game import MemoryGame  
            game = MemoryGame(game_config)
            
        elif game_name == 'balloon_pop':
            from games.balloon_pop import BalloonPopGame
            game = BalloonPopGame(game_config)
            
        elif game_name == 'fruit_ninja':
            from games.fruit_ninja_game import FruitNinjaGame
            game = FruitNinjaGame(game_config)
            
        else:
            print(f"Unknown game: {game_name}")
            return
            
        # Launch game
        game.run()
        
    except ImportError as e:
        print(f"Error importing game {game_name}: {e}")
    except Exception as e:
        print(f"Error launching game: {e}")

if __name__ == "__main__":
    # Load configuration
    selected_game = load_game_config()
    
    if selected_game:
        print(f"Launching {selected_game}...")
        launch_selected_game(selected_game)
    else:
        print("No game configured. Please reinstall the application.")
        input("Press Enter to exit...")