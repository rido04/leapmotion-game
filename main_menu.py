# main_menu.py
"""
Main menu for the Hand Tracking Game Collection
"""

import pygame
import sys
import math
import importlib
from core import *
from games import AVAILABLE_GAMES


class GameCard:
    """Animated card for each game in the menu"""
    def __init__(self, x, y, width, height, game_info):
        self.rect = pygame.Rect(x, y, width, height)
        self.game_info = game_info
        self.hovered = False
        self.animation_progress = 0
        self.hand_hover_time = 0
        self.hand_activated = False
        self.selected = False
        
        # Visual properties
        self.base_color = DARK_GRAY
        self.hover_color = game_info.get('preview_color', BLUE)
        self.current_color = self.base_color
        self.glow_intensity = 0
        
    def update(self, mouse_pos, hand_pos=None, hand_pinching=False):
        # Check hover state
        mouse_hovered = self.rect.collidepoint(mouse_pos)
        hand_hovered = False
        if hand_pos:
            hand_hovered = self.rect.collidepoint(hand_pos)
        
        self.hovered = mouse_hovered or hand_hovered
        
        # Hand activation logic
        if hand_hovered:
            if hand_pinching:
                self.hand_activated = True
            else:
                self.hand_hover_time += 0.016
                if self.hand_hover_time >= HAND_HOVER_TIME_THRESHOLD:
                    self.hand_activated = True
        else:
            self.hand_hover_time = 0
            self.hand_activated = False
        
        # Smooth animations
        target_progress = 1.0 if self.hovered else 0.0
        self.animation_progress += (target_progress - self.animation_progress) * 0.15
        
        # Update colors and glow
        self.glow_intensity = self.animation_progress * 255
        r = int(self.base_color[0] + (self.hover_color[0] - self.base_color[0]) * self.animation_progress * 0.3)
        g = int(self.base_color[1] + (self.hover_color[1] - self.base_color[1]) * self.animation_progress * 0.3)
        b = int(self.base_color[2] + (self.hover_color[2] - self.base_color[2]) * self.animation_progress * 0.3)
        self.current_color = (r, g, b)
    
    def draw(self, screen, font_medium, font_small, time_elapsed):
        # Draw glow effect
        if self.animation_progress > 0.1:
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20))
            glow_surface.set_alpha(int(self.glow_intensity * 0.3))
            pygame.draw.rect(glow_surface, self.hover_color, 
                           (0, 0, self.rect.width + 20, self.rect.height + 20), 
                           border_radius=20)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        
        # Draw main card
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=15)
        
        # Draw hover progress indicator
        if self.hand_hover_time > 0 and self.hand_hover_time < HAND_HOVER_TIME_THRESHOLD:
            progress_width = int((self.rect.width - 8) * (self.hand_hover_time / HAND_HOVER_TIME_THRESHOLD))
            progress_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, progress_width, 6)
            pygame.draw.rect(screen, YELLOW, progress_rect, border_radius=3)
        
        # Draw game icon/preview (simple geometric shape for now)
        icon_size = 60
        icon_x = self.rect.centerx
        icon_y = self.rect.y + 40
        
        # Animated icon based on game type
        if "Tic Tac Toe" in self.game_info['name']:
            # Draw animated tic-tac-toe grid
            grid_size = icon_size
            cell_size = grid_size // 3
            start_x = icon_x - grid_size // 2
            start_y = icon_y - grid_size // 2
            
            # Animated grid lines
            line_alpha = int(200 + math.sin(time_elapsed * 3) * 55)
            line_color = (*self.hover_color, line_alpha)
            
            for i in range(4):
                # Vertical lines
                x = start_x + i * cell_size
                pygame.draw.line(screen, WHITE, (x, start_y), (x, start_y + grid_size), 2)
                # Horizontal lines  
                y = start_y + i * cell_size
                pygame.draw.line(screen, WHITE, (start_x, y), (start_x + grid_size, y), 2)
        
        elif "Memory" in self.game_info['name']:
            # Draw card grid preview
            card_size = 15
            for i in range(2):
                for j in range(3):
                    card_x = icon_x - 30 + j * 20
                    card_y = icon_y - 15 + i * 20
                    
                    # Animated card flip effect
                    flip_progress = (math.sin(time_elapsed * 2 + i * j) + 1) * 0.5
                    card_color = self.hover_color if flip_progress > 0.5 else LIGHT_GRAY
                    
                    pygame.draw.rect(screen, card_color, 
                                   (card_x, card_y, card_size, card_size), 
                                   border_radius=3)
        
        else:
            # Default: animated circle
            pulse = math.sin(time_elapsed * 4) * 5 + icon_size // 2
            pygame.draw.circle(screen, self.hover_color, (icon_x, icon_y), int(pulse))
            pygame.draw.circle(screen, WHITE, (icon_x, icon_y), int(pulse), 3)
        
        # Draw game title
        title_surface = font_medium.render(self.game_info['name'], True, WHITE)
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.y + 110))
        screen.blit(title_surface, title_rect)
        
        # Draw description
        description = self.game_info.get('description', 'A fun game')
        desc_lines = self.wrap_text(description, font_small, self.rect.width - 20)
        
        for i, line in enumerate(desc_lines[:2]):  # Max 2 lines
            desc_surface = font_small.render(line, True, LIGHT_GRAY)
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, self.rect.y + 140 + i * 20))
            screen.blit(desc_surface, desc_rect)
    
    def wrap_text(self, text, font, max_width):
        """Simple text wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed
    
    def is_hand_activated(self):
        if self.hand_activated:
            self.hand_activated = False
            self.hand_hover_time = 0
            return True
        return False


class MainMenu:
    def __init__(self, auto_fullscreen=True):  # Add parameter
        pygame.init()
        
        # Auto fullscreen untuk retail/kiosk mode
        if auto_fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            self.fullscreen = True
            pygame.mouse.set_visible(False)  # Hide cursor untuk kiosk mode
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.fullscreen = False
        
        pygame.display.set_caption("Hand Tracking Games - Main Menu")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.setup_fonts()
        self.hand_tracker = HandTracker()
        self.background_manager = BackgroundManager()
        self.particle_system = ParticleSystem()
        self.logo_manager = LogoManager()
        
        # Menu state
        self.running = True
        self.selected_game = None
        self.time_elapsed = 0
        
        # Create game cards
        self.create_game_cards()
        
        # Create UI buttons (adjust position jika fullscreen)
        self.create_ui_buttons()
        
    def setup_fonts(self):
        self.font_title = pygame.font.Font(None, FONT_TITLE)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
    def create_game_cards(self):
        """Create cards for available games"""
        self.game_cards = []
        
        # Use games from registry
        games_info = AVAILABLE_GAMES
        
        # Calculate card layout
        cards_per_row = 2
        card_width = 250
        card_height = 200
        card_spacing_x = 50
        card_spacing_y = 50
        
        total_width = cards_per_row * card_width + (cards_per_row - 1) * card_spacing_x
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = 300
        
        for i, game_info in enumerate(games_info):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + card_spacing_x)
            y = start_y + row * (card_height + card_spacing_y)
            
            card = GameCard(x, y, card_width, card_height, game_info)
            self.game_cards.append(card)
    
    def create_ui_buttons(self):
        """Create menu UI buttons - adjust position based on screen size"""
        button_y = 20
        current_width = self.screen.get_width()  # Get actual screen width
        
        self.fullscreen_button = AnimatedButton(
            current_width - 140, button_y, 130, 50,
            "🪟 Windowed" if self.fullscreen else "🖥️ Fullscreen", 
            GREEN_DARK, GREEN
        )
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            
            # Update button position
            self.fullscreen_button.rect.x = info.current_w - 140
            self.fullscreen_button.text = "🪟 Windowed"
            
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            
            # Reset button position
            self.fullscreen_button.rect.x = WINDOW_WIDTH - 140
            self.fullscreen_button.text = "🖥️ Fullscreen"
    
    def launch_game(self, game_info):
        """Launch selected game"""
        try:
            print(f"Launching {game_info['name']}...")
            
            # Import game module
            module = importlib.import_module(game_info['module'])
            game_class = getattr(module, game_info['class'])
            
            # Create and run game
            game_instance = game_class(self.screen)
            result = game_instance.run()
            
            # Handle return from game
            if result == "quit":
                self.running = False
            # If result is "menu", continue with menu loop
            
        except ImportError as e:
            print(f"Error importing {game_info['module']}: {e}")
            print("Game not yet implemented!")
        except AttributeError as e:
            print(f"Error finding class {game_info['class']}: {e}")
        except Exception as e:
            print(f"Error launching game: {e}")
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check UI button clicks
                if self.fullscreen_button.is_clicked(event.pos, True):
                    self.toggle_fullscreen()
                else:
                    # Check game card clicks
                    for card in self.game_cards:
                        if card.is_clicked(event.pos, True):
                            self.launch_game(card.game_info)
    
    def update(self):
        self.time_elapsed += 0.016
        
        mouse_pos = pygame.mouse.get_pos()
        hand_data = self.hand_tracker.hand_data
        
        # Use hand position if available
        hand_pos = None
        if hand_data.active and hand_data.hands_count > 0:
            hand_pos = (hand_data.x, hand_data.y)
        
        # Update game cards
        for card in self.game_cards:
            card.update(mouse_pos, hand_pos, hand_data.pinching)
            
            # Check for hand activation
            if card.is_hand_activated():
                self.launch_game(card.game_info)
        
        # Update UI buttons
        self.fullscreen_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Check for hand-activated buttons
        if self.fullscreen_button.is_hand_activated():
            self.toggle_fullscreen()
            print("Fullscreen toggled by hand gesture!")
    
    def draw(self):
        # Draw background
        self.background_manager.draw(self.screen)
        
        # Draw particles
        self.particle_system.update(self.screen.get_width(), self.screen.get_height())
        self.particle_system.draw(self.screen)
        
        # Draw logos
        self.logo_manager.draw(self.screen)
        
        # Draw title
        title_text = self.font_title.render("HAND TRACKING GAMES", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.font_small.render("Choose a game by clicking or pinching", True, CYAN)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw game cards
        for card in self.game_cards:
            card.draw(self.screen, self.font_medium, self.font_small, self.time_elapsed)
        
        # Draw UI buttons
        self.fullscreen_button.draw(self.screen, self.font_small)
        
        # Draw hand tracking status
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            # Draw hand indicator
            pulse = math.sin(self.time_elapsed * 6) * 3 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
            
            # Status text
            status = f"✋ Hand Tracking: {hand_data.hands_count} hands detected"
            status_color = GREEN
        else:
            status = "🖱️ Using mouse (no hand tracking)"
            status_color = LIGHT_GRAY
        
        status_text = self.font_small.render(status, True, status_color)
        status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        self.screen.blit(status_text, status_rect)
        
        # Instructions
        instructions = [
            "🎯 Hover over game cards and PINCH to select | 🖱️ Mouse click also works",
            "🔄 Hover over buttons for 1 sec or PINCH | F11: Fullscreen | B: Background | ESC: Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 20).render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80 + i * 20))
            self.screen.blit(text, text_rect)
    
    def run(self):
        print("Starting Main Menu...")
        self.hand_tracker.start()
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.hand_tracker.stop()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()