# games/base_game.py
"""
Abstract base class for all games
Provides common functionality and structure
Updated: Removed fullscreen functionality, repositioned menu button
"""

import pygame
import sys
from abc import ABC, abstractmethod
from core import *


class BaseGame(ABC):
    def __init__(self, screen=None):
        # Initialize pygame if not already done
        if not pygame.get_init():
            pygame.init()
            
        # Screen setup
        if screen is None:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        else:
            self.screen = screen
            
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.setup_fonts()
        
        # Core systems
        self.hand_tracker = HandTracker()
        self.background_manager = BackgroundManager()
        self.particle_system = ParticleSystem()
        self.logo_manager = LogoManager()
        
        # Control states
        self.running = True
        self.exit_to_menu = False
        
        # UI buttons (common to all games) - will be created with dynamic positions
        self.create_common_ui()
        
    def setup_fonts(self):
        """Initialize pygame fonts"""
        self.font_title = pygame.font.Font(None, FONT_TITLE)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
    
    def get_current_screen_size(self):
        """Get current screen dimensions"""
        return self.screen.get_width(), self.screen.get_height()
        
    def create_common_ui(self):
        """Create UI buttons common to all games - uses dynamic screen size"""
        current_width, current_height = self.get_current_screen_size()
        button_y = 20
        
        # Only back button now, positioned more centrally in top right
        self.back_button = AnimatedButton(
            current_width - 140, button_y, 120, 50, 
            "🏠 Menu", RED_DARK, RED
        )
    
    def recalculate_common_ui(self):
        """Recalculate common UI positions when screen size changes"""
        print("Recalculating common UI for new screen size...")
        self.create_common_ui()
    
    def handle_common_events(self, event):
        """Handle events common to all games"""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_to_menu = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check common button clicks (only back button now)
            if self.back_button.is_clicked(event.pos, True):
                self.exit_to_menu = True
    
    def update_common_ui(self):
        """Update common UI elements"""
        mouse_pos = pygame.mouse.get_pos()
        hand_data = self.hand_tracker.hand_data
        
        # Use hand position if available, otherwise mouse
        hand_pos = None
        if hand_data.active and hand_data.hands_count > 0:
            hand_pos = (hand_data.x, hand_data.y)
        
        # Update back button only
        self.back_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Check for hand activation
        if self.back_button.is_hand_activated():
            self.exit_to_menu = True
            print("Back to menu by hand gesture!")
    
    def draw_common_elements(self):
        """Draw elements common to all games"""
        current_width, current_height = self.get_current_screen_size()
        
        # Background
        self.background_manager.draw(self.screen)
        
        # Particles
        self.particle_system.update(current_width, current_height)
        self.particle_system.draw(self.screen)
        
        # Logos
        self.logo_manager.draw(self.screen)
        
        # Common buttons (only back button now)
        self.back_button.draw(self.screen, self.font_small)
    
    def start_game(self):
        """Start the game - called before main loop"""
        print(f"Starting {self.__class__.__name__}...")
        print(f"Game screen size: {self.get_current_screen_size()}")
        self.hand_tracker.start()
        
    def cleanup(self):
        """Cleanup when game ends"""
        print(f"Stopping {self.__class__.__name__}...")
        self.hand_tracker.stop()
        
    def run(self):
        """Main game loop - calls abstract methods"""
        self.start_game()
        
        while self.running and not self.exit_to_menu:
            # Handle events
            for event in pygame.event.get():
                self.handle_common_events(event)
                game_result = self.handle_game_events(event)  # Game-specific events
                
                # Handle game-specific navigation
                if game_result == "main_menu":
                    self.exit_to_menu = True
            
            # Update game state
            game_result = self.update_game()  # Game-specific update
            if game_result == "main_menu":
                self.exit_to_menu = True
                
            self.update_common_ui()
            
            # Render everything
            self.draw_common_elements()
            self.draw_game()  # Game-specific drawing
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.cleanup()
        return "menu" if self.exit_to_menu else "quit"
    
    # Abstract methods that each game must implement
    @abstractmethod
    def handle_game_events(self, event):
        """Handle game-specific events"""
        pass
    
    @abstractmethod
    def update_game(self):
        """Update game-specific state"""
        pass
    
    @abstractmethod
    def draw_game(self):
        """Draw game-specific elements"""
        pass
    
    @abstractmethod
    def get_game_info(self):
        """Return game info for menu display"""
        return {
            'name': 'Unknown Game',
            'description': 'A game',
            'preview_color': CYAN
        }