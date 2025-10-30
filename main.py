# main.py (Updated with command line support)
import sys
import os
import configparser
from pathlib import Path

def load_game_config(config_file_name='game_config.ini'):
    """Load game configuration from specified config file"""
    config_file = Path(config_file_name)
    
    if not config_file.exists():
        print(f"Configuration file '{config_file_name}' not found!")
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
        
        print(f"Loading {game_name}...")
        
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
        
        elif game_name == 'object_catcher':
            from games.object_catcher_game import ObjectCatcherGame
            game = ObjectCatcherGame(game_config)
            
        else:
            print(f"Unknown game: {game_name}")
            return
            
        # Launch game
        print(f"Starting {game_name}...")
        game.run()
        
    except ImportError as e:
        print(f"Error importing game '{game_name}': {e}")
        print("Make sure all game files are properly installed.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Error launching game: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("=" * 50)
    print("Adidas Interactive Games Launcher")
    print("=" * 50)
    
    # Check if config file specified via command line
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        print(f"Using config file: {config_file}")
    else:
        config_file = 'game_config.ini'
        print(f"Using default config file: {config_file}")
    
    # Load configuration
    game_config = load_game_config(config_file)
    
    if game_config:
        print(f"Configuration loaded successfully!")
        print(f"Game: {game_config['selected_game']}")
        print(f"Fullscreen: {game_config['fullscreen']}")
        print(f"Kiosk Mode: {game_config['kiosk_mode']}")
        print("-" * 50)
        
        launch_selected_game(game_config)
    else:
        print("ERROR: No valid game configuration found!")
        print("Please reinstall the application or check your config files.")
        input("Press Enter to exit...")