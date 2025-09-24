# main_menu.py
"""
Optimized Main menu for the Hand Tracking Game Collection
Reduced animations for better performance while keeping icons and layout
"""

import pygame
import sys
import math
import importlib
from core import *
from games import AVAILABLE_GAMES


class GameCard:
    """Optimized card for each game in the menu with PNG icons"""
    def __init__(self, x, y, width, height, game_info):
        self.rect = pygame.Rect(x, y, width, height)
        self.game_info = game_info
        self.hovered = False
        self.hand_hover_time = 0
        self.hand_activated = False
        self.selected = False
        
        # Simplified visual properties
        self.base_color = (30, 30, 35)
        self.hover_color = game_info.get('preview_color', BLUE)
        self.current_color = self.base_color
        self.hover_alpha = 0.0  # Simple alpha blend instead of complex animations
        
        # Load icon image
        self.icon_image = None
        self.icon_size = (64, 64)
        self.load_icon()
        
        # Pre-rendered surfaces for better performance
        self.title_surface = None
        self.desc_surfaces = []
        self.render_text()
        
    def load_icon(self):
        """Load PNG icon for the game"""
        icon_mapping = {
            'Tic Tac Toe': 'tic-tac-toe.png',
            'Memory Game': 'memory-card.png',
            'Balloon Pop': 'balloon.png',
            'Fruit Slash': 'fruit.png',
        }
        
        game_name = self.game_info['name']
        icon_filename = None
        
        for key, filename in icon_mapping.items():
            if key in game_name:
                icon_filename = filename
                break
        
        if icon_filename:
            try:
                icon_path = f'assets/icon/games/{icon_filename}'
                original_icon = pygame.image.load(icon_path).convert_alpha()
                self.icon_image = pygame.transform.smoothscale(original_icon, self.icon_size)
                print(f"Loaded icon for {game_name}: {icon_filename}")
            except Exception as e:
                print(f"Could not load icon {icon_filename}: {e}")
                self.create_fallback_icon()
        else:
            print(f"No icon mapping found for {game_name}")
            self.create_fallback_icon()
    
    def create_fallback_icon(self):
        """Create a fallback icon if PNG loading fails"""
        self.icon_image = pygame.Surface(self.icon_size, pygame.SRCALPHA)
        pygame.draw.circle(self.icon_image, self.hover_color, 
                          (self.icon_size[0]//2, self.icon_size[1]//2), 
                          self.icon_size[0]//2 - 5)
        pygame.draw.circle(self.icon_image, WHITE, 
                          (self.icon_size[0]//2, self.icon_size[1]//2), 
                          self.icon_size[0]//2 - 5, 3)
    
    def render_text(self):
        """Pre-render text surfaces for better performance"""
        font_medium = pygame.font.Font(None, FONT_MEDIUM)
        font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Pre-render title
        self.title_surface = font_medium.render(self.game_info['name'], True, WHITE)
        self.title_hover_surface = font_medium.render(self.game_info['name'], True, self.hover_color)
        
        # Pre-render description lines
        description = self.game_info.get('description', 'A fun game')
        desc_lines = self.wrap_text(description, font_small, self.rect.width - 20)
        
        self.desc_surfaces = []
        for line in desc_lines[:2]:  # Max 2 lines
            normal_surface = font_small.render(line, True, (200, 200, 220))
            hover_surface = font_small.render(line, True, WHITE)
            self.desc_surfaces.append((normal_surface, hover_surface))
        
    def update_position(self, x, y):
        """Update card position"""
        self.rect.x = x
        self.rect.y = y
        
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
        
        # Simple alpha animation instead of complex effects
        target_alpha = 1.0 if self.hovered else 0.0
        self.hover_alpha += (target_alpha - self.hover_alpha) * 0.15
        
        # Simplified color blending
        if self.hover_alpha > 0:
            blend_factor = self.hover_alpha * 0.3
            r = int(self.base_color[0] + (self.hover_color[0] - self.base_color[0]) * blend_factor)
            g = int(self.base_color[1] + (self.hover_color[1] - self.base_color[1]) * blend_factor)
            b = int(self.base_color[2] + (self.hover_color[2] - self.base_color[2]) * blend_factor)
            self.current_color = (r, g, b)
        else:
            self.current_color = self.base_color
    
    def draw(self, screen):
        # Draw simple shadow (no complex shadow effects)
        shadow_rect = self.rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(screen, (10, 10, 15), shadow_rect, border_radius=18)
        
        # Draw main card
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=18)
        
        # Simple border
        border_color = WHITE if self.hover_alpha < 0.5 else self.hover_color
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=18)
        
        # Draw hover progress indicator (simplified)
        if self.hand_hover_time > 0 and self.hand_hover_time < HAND_HOVER_TIME_THRESHOLD:
            progress_width = int((self.rect.width - 12) * (self.hand_hover_time / HAND_HOVER_TIME_THRESHOLD))
            progress_rect = pygame.Rect(self.rect.x + 6, self.rect.y + 6, progress_width, 4)
            pygame.draw.rect(screen, YELLOW, progress_rect, border_radius=2)
        
        # Draw icon (no scaling or rotation effects for performance)
        if self.icon_image:
            icon_x = self.rect.centerx - self.icon_size[0] // 2
            icon_y = self.rect.y + 35
            screen.blit(self.icon_image, (icon_x, icon_y))
        
        # Draw pre-rendered title
        title_surface = self.title_hover_surface if self.hover_alpha > 0.5 else self.title_surface
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.y + 125))
        screen.blit(title_surface, title_rect)
        
        # Draw pre-rendered description
        for i, (normal_surf, hover_surf) in enumerate(self.desc_surfaces):
            desc_surface = hover_surf if self.hover_alpha > 0.3 else normal_surf
            desc_rect = desc_surface.get_rect(center=(self.rect.centerx, self.rect.y + 150 + i * 18))
            screen.blit(desc_surface, desc_rect)
    
    def wrap_text(self, text, font, max_width):
        """Text wrapping helper"""
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
                else:
                    lines.append(word)
        
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
    def __init__(self, auto_fullscreen=True):
        pygame.init()
        
        # Always start in fullscreen
        info = pygame.display.Info()
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        
        pygame.display.set_caption("Hand Tracking Games")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.setup_fonts()
        self.hand_tracker = HandTracker()
        self.background_manager = VideoBackgroundManager()
        self.particle_system = ParticleSystem()
        self.logo_manager = LogoManager()
        
        # Menu state
        self.running = True
        self.selected_game = None
        self.time_elapsed = 0
        
        # Simplified visual effects
        self.menu_fade_in = 0
        
        # Create game cards
        self.game_cards = []
        self.create_game_cards()
        
        # Pre-render static text elements
        self.render_static_text()
        
    def render_static_text(self):
        """Pre-render text that doesn't change for better performance"""
        current_width, current_height = self.get_current_screen_size()
        
        # Pre-render title
        self.title_surface = self.font_title.render("HAND TRACKING GAMES", True, WHITE)
        self.title_rect = self.title_surface.get_rect(center=(current_width // 2, 80))
        
        # Pre-render subtitle
        self.subtitle_surface = self.font_small.render("Choose a game by clicking or pinching", True, (150, 200, 255))
        self.subtitle_rect = self.subtitle_surface.get_rect(center=(current_width // 2, 120))
        
        # Pre-render instructions
        self.instruction_surfaces = []
        instructions = [
            "Hover over game cards and PINCH to select | Mouse click also works",
            "Hover over buttons for 1 sec or PINCH | ESC: Exit"
        ]
        
        instruction_font = pygame.font.Font(None, 22)
        for i, instruction in enumerate(instructions):
            surface = instruction_font.render(instruction, True, (120, 140, 160))
            rect = surface.get_rect(center=(current_width // 2, current_height - 100 + i * 25))
            self.instruction_surfaces.append((surface, rect))
        
        # Pre-render version
        version_text = "Developed and maintained by MCMMediaNetworks development team"
        self.version_surface = pygame.font.Font(None, 18).render(version_text, True, (80, 100, 120))
        self.version_rect = self.version_surface.get_rect(bottomright=(current_width - 20, current_height - 10))
        
    def setup_fonts(self):
        self.font_title = pygame.font.Font(None, FONT_TITLE + 10)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
    def get_current_screen_size(self):
        """Get current screen dimensions"""
        return self.screen.get_width(), self.screen.get_height()
        
    def create_game_cards(self):
        """Create cards for available games with optimized positioning"""
        self.game_cards.clear()
        
        current_width, current_height = self.get_current_screen_size()
        games_info = AVAILABLE_GAMES
        
        # Card layout
        cards_per_row = 2
        card_width = 300
        card_height = 220
        card_spacing_x = 80
        card_spacing_y = 60
        
        total_width = cards_per_row * card_width + (cards_per_row - 1) * card_spacing_x
        total_height = ((len(games_info) + cards_per_row - 1) // cards_per_row) * card_height + \
                      (((len(games_info) + cards_per_row - 1) // cards_per_row) - 1) * card_spacing_y
        
        start_x = (current_width - total_width) // 2
        start_y = max(200, (current_height - total_height) // 2 - 30)
        
        print(f"Card layout: {total_width}x{total_height} at ({start_x}, {start_y})")
        
        for i, game_info in enumerate(games_info):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + card_spacing_x)
            y = start_y + row * (card_height + card_spacing_y)
            
            card = GameCard(x, y, card_width, card_height, game_info)
            self.game_cards.append(card)
    
    def launch_game(self, game_info):
        """Launch selected game"""
        try:
            print(f"Launching {game_info['name']}...")
            
            module = importlib.import_module(game_info['module'])
            game_class = getattr(module, game_info['class'])
            
            game_instance = game_class(self.screen)
            result = game_instance.run()
            
            if result == "quit":
                self.running = False
                
        except ImportError as e:
            print(f"Error importing {game_info['module']}: {e}")
        except AttributeError as e:
            print(f"Error finding class {game_info['class']}: {e}")
        except Exception as e:
            print(f"Error launching game: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for card in self.game_cards:
                    if card.is_clicked(event.pos, True):
                        self.launch_game(card.game_info)
    
    def update(self):
        dt = 0.016
        self.time_elapsed += dt
        
        # Simple fade-in animation
        self.menu_fade_in = min(1.0, self.menu_fade_in + dt * 2.0)
        
        mouse_pos = pygame.mouse.get_pos()
        hand_data = self.hand_tracker.hand_data
        
        hand_pos = None
        if hand_data.active and hand_data.hands_count > 0:
            hand_pos = (hand_data.x, hand_data.y)
        
        # Update game cards (optimized)
        for card in self.game_cards:
            card.update(mouse_pos, hand_pos, hand_data.pinching)
            
            if card.is_hand_activated():
                self.launch_game(card.game_info)
    
    def draw(self):
        current_width, current_height = self.get_current_screen_size()
        
        # Draw background
        self.background_manager.draw(self.screen)
        
        # Draw particles (reduced update frequency for performance)
        if self.time_elapsed % 3 < 0.016:  # Update every 3rd frame
            self.particle_system.update(current_width, current_height)
        self.particle_system.draw(self.screen)
        
        # Draw logos
        self.logo_manager.draw(self.screen)
        
        # Draw pre-rendered title (no glow effects)
        self.screen.blit(self.title_surface, self.title_rect)
        
        # Draw subtitle
        self.screen.blit(self.subtitle_surface, self.subtitle_rect)
        
        # Draw game cards (simplified)
        for card in self.game_cards:
            card.draw(self.screen)
        
        # Draw hand tracking indicator (simplified)
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            # Simple hand indicator without complex effects
            hand_color = (0, 255, 100) if not hand_data.pinching else (255, 255, 0)
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), 8)
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), 8, 2)
            
            status = f"Hand Tracking: {hand_data.hands_count} hands detected"
            status_color = (0, 255, 150)
        else:
            status = "Using mouse (no hand tracking)"
            status_color = (150, 150, 170)
        
        # Draw status
        status_surface = self.font_small.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(current_width // 2, current_height - 60))
        
        # Simple status background
        status_bg = pygame.Rect(status_rect.x - 10, status_rect.y - 5, 
                              status_rect.width + 20, status_rect.height + 10)
        pygame.draw.rect(self.screen, (20, 20, 30), status_bg, border_radius=5)
        self.screen.blit(status_surface, status_rect)
        
        # Draw pre-rendered instructions
        for surface, rect in self.instruction_surfaces:
            # Simple instruction background
            inst_bg = pygame.Rect(rect.x - 8, rect.y - 3, 
                                rect.width + 16, rect.height + 6)
            pygame.draw.rect(self.screen, (15, 15, 25), inst_bg, border_radius=3)
            self.screen.blit(surface, rect)
        
        # Draw version
        self.screen.blit(self.version_surface, self.version_rect)
    
    def run(self):
        print("Starting Optimized Main Menu...")
        print(f"Screen size: {self.get_current_screen_size()}")
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