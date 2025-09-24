# main_menu.py
"""
Enhanced Main menu for the Hand Tracking Game Collection
Improved with PNG icons from assets/icon/games folder
Dark theme with better visual design
"""

import pygame
import sys
import math
import importlib
from core import *
from games import AVAILABLE_GAMES


class GameCard:
    """Enhanced animated card for each game in the menu with PNG icons"""
    def __init__(self, x, y, width, height, game_info):
        self.rect = pygame.Rect(x, y, width, height)
        self.game_info = game_info
        self.hovered = False
        self.animation_progress = 0
        self.hand_hover_time = 0
        self.hand_activated = False
        self.selected = False
        
        # Visual properties
        self.base_color = (30, 30, 35)  # Darker base color
        self.hover_color = game_info.get('preview_color', BLUE)
        self.current_color = self.base_color
        self.glow_intensity = 0
        
        # Enhanced visual effects
        self.card_scale = 1.0
        self.shadow_offset = 5
        self.border_glow = 0
        
        # Load icon image
        self.icon_image = None
        self.icon_size = (64, 64)  # Target icon size
        self.load_icon()
        
    def load_icon(self):
        """Load PNG icon for the game"""
        # Map game names to icon files
        icon_mapping = {
            'Tic Tac Toe': 'tic-tac-toe.png',
            'Memory Game': 'memory-card.png',
            'Balloon Pop': 'balloon.png',
            'Fruit Slash': 'fruit.png',
        }
        
        game_name = self.game_info['name']
        icon_filename = None
        
        # Find matching icon
        for key, filename in icon_mapping.items():
            if key in game_name:
                icon_filename = filename
                break
        
        if icon_filename:
            try:
                icon_path = f'assets/icon/games/{icon_filename}'
                original_icon = pygame.image.load(icon_path).convert_alpha()
                # Scale down from 500x500 to 64x64 for better performance
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
        
    def update_position(self, x, y):
        """Update card position - for layout recalculation"""
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
        
        # Enhanced smooth animations
        target_progress = 1.0 if self.hovered else 0.0
        self.animation_progress += (target_progress - self.animation_progress) * 0.12
        
        # Enhanced visual effects
        self.card_scale = 1.0 + self.animation_progress * 0.05
        self.glow_intensity = self.animation_progress * 255
        self.border_glow = self.animation_progress * 100
        
        # Update colors with enhanced blending
        blend_factor = self.animation_progress * 0.4
        r = int(self.base_color[0] + (self.hover_color[0] - self.base_color[0]) * blend_factor)
        g = int(self.base_color[1] + (self.hover_color[1] - self.base_color[1]) * blend_factor)
        b = int(self.base_color[2] + (self.hover_color[2] - self.base_color[2]) * blend_factor)
        self.current_color = (r, g, b)
    
    def draw(self, screen, font_medium, font_small, time_elapsed):
        # Calculate scaled rect for hover effect
        if abs(self.card_scale - 1.0) > 0.01:
            scaled_width = int(self.rect.width * self.card_scale)
            scaled_height = int(self.rect.height * self.card_scale)
            scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
            scaled_rect.center = self.rect.center
        else:
            scaled_rect = self.rect
        
        # Draw enhanced shadow
        shadow_color = (10, 10, 15, int(50 + self.animation_progress * 30))
        shadow_rect = scaled_rect.copy()
        shadow_rect.move_ip(self.shadow_offset, self.shadow_offset)
        
        # Create shadow surface
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), 
                        (0, 0, shadow_rect.width, shadow_rect.height), 
                        border_radius=20)
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw enhanced glow effect
        if self.animation_progress > 0.1:
            glow_size = 30
            glow_surface = pygame.Surface((scaled_rect.width + glow_size, scaled_rect.height + glow_size), 
                                        pygame.SRCALPHA)
            glow_alpha = int(self.glow_intensity * 0.4)
            
            # Multi-layered glow
            for i in range(3):
                glow_radius = 20 + i * 5
                glow_color = (*self.hover_color, glow_alpha // (i + 1))
                pygame.draw.rect(glow_surface, (*self.hover_color, glow_alpha // (i + 2)), 
                               (i * 2, i * 2, scaled_rect.width + glow_size - i * 4, 
                                scaled_rect.height + glow_size - i * 4), 
                               border_radius=25 + i * 2)
            
            screen.blit(glow_surface, (scaled_rect.x - glow_size//2, scaled_rect.y - glow_size//2), 
                       special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw main card with gradient effect
        pygame.draw.rect(screen, self.current_color, scaled_rect, border_radius=18)
        
        # Enhanced border
        border_color = (255, 255, 255, int(180 + self.border_glow))
        pygame.draw.rect(screen, WHITE, scaled_rect, 3, border_radius=18)
        
        # Draw hover progress indicator
        if self.hand_hover_time > 0 and self.hand_hover_time < HAND_HOVER_TIME_THRESHOLD:
            progress_width = int((scaled_rect.width - 12) * (self.hand_hover_time / HAND_HOVER_TIME_THRESHOLD))
            progress_rect = pygame.Rect(scaled_rect.x + 6, scaled_rect.y + 6, progress_width, 4)
            pygame.draw.rect(screen, YELLOW, progress_rect, border_radius=2)
            
            # Progress glow
            glow_rect = pygame.Rect(scaled_rect.x + 6, scaled_rect.y + 4, progress_width, 8)
            pygame.draw.rect(screen, (255, 255, 0, 100), glow_rect, border_radius=4)
        
        # Draw PNG icon with enhanced effects
        if self.icon_image:
            # Calculate icon position
            icon_x = scaled_rect.centerx - self.icon_size[0] // 2
            icon_y = scaled_rect.y + 35
            
            # Enhanced icon effects when hovered
            if self.animation_progress > 0.1:
                # Icon scaling and rotation
                icon_scale = 1.0 + self.animation_progress * 0.1
                rotation_angle = math.sin(time_elapsed * 3) * self.animation_progress * 5
                
                if abs(icon_scale - 1.0) > 0.01 or abs(rotation_angle) > 1:
                    # Apply scaling
                    scaled_icon_size = (int(self.icon_size[0] * icon_scale), 
                                      int(self.icon_size[1] * icon_scale))
                    scaled_icon = pygame.transform.smoothscale(self.icon_image, scaled_icon_size)
                    
                    # Apply rotation
                    if abs(rotation_angle) > 1:
                        rotated_icon = pygame.transform.rotate(scaled_icon, rotation_angle)
                        icon_rect = rotated_icon.get_rect(center=(scaled_rect.centerx, icon_y + self.icon_size[1]//2))
                    else:
                        icon_rect = scaled_icon.get_rect(center=(scaled_rect.centerx, icon_y + self.icon_size[1]//2))
                        rotated_icon = scaled_icon
                    
                    # Draw icon glow
                    glow_surface = rotated_icon.copy()
                    glow_surface.fill((*self.hover_color, int(self.animation_progress * 150)), special_flags=pygame.BLEND_ADD)
                    glow_rect = icon_rect.copy()
                    glow_rect.inflate_ip(4, 4)
                    screen.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
                    
                    screen.blit(rotated_icon, icon_rect)
                else:
                    screen.blit(self.icon_image, (icon_x, icon_y))
            else:
                screen.blit(self.icon_image, (icon_x, icon_y))
        
        # Draw game title with enhanced typography
        title_color = WHITE if self.animation_progress < 0.5 else self.hover_color
        title_surface = font_medium.render(self.game_info['name'], True, title_color)
        title_rect = title_surface.get_rect(center=(scaled_rect.centerx, scaled_rect.y + 125))
        
        # Title shadow
        shadow_surface = font_medium.render(self.game_info['name'], True, (0, 0, 0))
        shadow_rect = title_rect.copy()
        shadow_rect.move_ip(1, 1)
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)
        
        # Draw enhanced description
        description = self.game_info.get('description', 'A fun game')
        desc_lines = self.wrap_text(description, font_small, scaled_rect.width - 20)
        
        desc_color = (200, 200, 220) if self.animation_progress < 0.3 else (255, 255, 255)
        for i, line in enumerate(desc_lines[:2]):  # Max 2 lines
            desc_surface = font_small.render(line, True, desc_color)
            desc_rect = desc_surface.get_rect(center=(scaled_rect.centerx, scaled_rect.y + 150 + i * 18))
            screen.blit(desc_surface, desc_rect)
    
    def wrap_text(self, text, font, max_width):
        """Enhanced text wrapping with better word handling"""
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
                    # Word too long, force it
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
        
        # Always start in fullscreen for kiosk/retail mode
        info = pygame.display.Info()
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)  # Hide cursor for kiosk mode
        
        pygame.display.set_caption("Hand Tracking Games")
        self.clock = pygame.time.Clock()
        
        # Enhanced visual elements - remove custom background colors
        # Let the original background manager handle the background
        
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
        
        # Enhanced visual effects
        self.title_glow = 0
        self.menu_fade_in = 0
        
        # Create game cards
        self.game_cards = []
        self.create_game_cards()
        
    def create_background_texture(self):
        """This function is no longer used - background handled by background_manager"""
        pass
        
    def setup_fonts(self):
        self.font_title = pygame.font.Font(None, FONT_TITLE + 10)  # Slightly larger
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
    def get_current_screen_size(self):
        """Get current screen dimensions"""
        return self.screen.get_width(), self.screen.get_height()
        
    def create_game_cards(self):
        """Create enhanced cards for available games with better positioning"""
        self.game_cards.clear()
        
        current_width, current_height = self.get_current_screen_size()
        
        # Use games from registry
        games_info = AVAILABLE_GAMES
        
        # Enhanced card layout
        cards_per_row = 2
        card_width = 300  # Wider cards for better icon display
        card_height = 220  # Taller for better proportions
        card_spacing_x = 80
        card_spacing_y = 60
        
        total_width = cards_per_row * card_width + (cards_per_row - 1) * card_spacing_x
        total_height = ((len(games_info) + cards_per_row - 1) // cards_per_row) * card_height + \
                      (((len(games_info) + cards_per_row - 1) // cards_per_row) - 1) * card_spacing_y
        
        # Better centering
        start_x = (current_width - total_width) // 2
        start_y = (current_height - total_height) // 2 - 30
        
        # Ensure minimum Y position
        min_y = 200
        if start_y < min_y:
            start_y = min_y
        
        print(f"Enhanced card layout: {total_width}x{total_height} at ({start_x}, {start_y})")
        print(f"Screen size: {current_width}x{current_height}")
        
        for i, game_info in enumerate(games_info):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + card_spacing_x)
            y = start_y + row * (card_height + card_spacing_y)
            
            card = GameCard(x, y, card_width, card_height, game_info)
            self.game_cards.append(card)
    
    def launch_game(self, game_info):
        """Launch selected game with enhanced feedback"""
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check game card clicks
                for card in self.game_cards:
                    if card.is_clicked(event.pos, True):
                        self.launch_game(card.game_info)
    
    def update(self):
        dt = 0.016
        self.time_elapsed += dt
        
        # Enhanced menu animations
        self.title_glow += dt * 2
        self.menu_fade_in = min(1.0, self.menu_fade_in + dt * 0.5)
        
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
    
    def draw(self):
        # Get current screen size for dynamic positioning
        current_width, current_height = self.get_current_screen_size()
        
        # Draw original background using background_manager
        self.background_manager.draw(self.screen)
        
        # Draw enhanced particles
        self.particle_system.update(current_width, current_height)
        self.particle_system.draw(self.screen)
        
        # Draw logos with fade-in
        alpha_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        self.logo_manager.draw(alpha_surface)
        alpha_surface.set_alpha(int(255 * self.menu_fade_in))
        self.screen.blit(alpha_surface, (0, 0))
        
        # Draw enhanced title with glow effect
        title_base_color = (255, 255, 255)
        title_glow_intensity = 0.3 + 0.2 * math.sin(self.title_glow)
        title_glow_color = (100, 150, 255)
        
        title_text = "HAND TRACKING GAMES"
        
        # Draw title glow layers
        for offset in range(3, 0, -1):
            glow_alpha = int(80 * title_glow_intensity / offset)
            glow_surface = self.font_title.render(title_text, True, (*title_glow_color, glow_alpha))
            glow_rect = glow_surface.get_rect(center=(current_width // 2 + offset, 80 + offset))
            
            # Apply glow
            glow_temp = pygame.Surface(glow_surface.get_size(), pygame.SRCALPHA)
            glow_temp.blit(glow_surface, (0, 0))
            self.screen.blit(glow_temp, glow_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw main title
        main_title = self.font_title.render(title_text, True, title_base_color)
        title_rect = main_title.get_rect(center=(current_width // 2, 80))
        self.screen.blit(main_title, title_rect)
        
        # Draw enhanced subtitle
        subtitle_text = "Choose a game by clicking or pinching"
        subtitle_surface = self.font_small.render(subtitle_text, True, (150, 200, 255))
        subtitle_rect = subtitle_surface.get_rect(center=(current_width // 2, 120))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw game cards with fade-in
        for i, card in enumerate(self.game_cards):
            card_alpha = min(1.0, self.menu_fade_in + i * 0.1)
            if card_alpha < 1.0:
                # Create temporary surface for alpha blending
                card_surface = pygame.Surface((card.rect.width + 100, card.rect.height + 100), pygame.SRCALPHA)
                temp_screen_pos = (card.rect.x - 50, card.rect.y - 50)
                
                # Draw card on temporary surface
                temp_card = GameCard(50, 50, card.rect.width, card.rect.height, card.game_info)
                temp_card.animation_progress = card.animation_progress
                temp_card.current_color = card.current_color
                temp_card.glow_intensity = card.glow_intensity
                temp_card.border_glow = card.border_glow
                temp_card.card_scale = card.card_scale
                temp_card.icon_image = card.icon_image
                temp_card.hand_hover_time = card.hand_hover_time
                
                temp_card.draw(card_surface, self.font_medium, self.font_small, self.time_elapsed)
                card_surface.set_alpha(int(255 * card_alpha))
                self.screen.blit(card_surface, temp_screen_pos)
            else:
                card.draw(self.screen, self.font_medium, self.font_small, self.time_elapsed)
        
        # Draw enhanced hand tracking indicator
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            # Enhanced hand indicator with trail effect
            pulse = math.sin(self.time_elapsed * 8) * 3 + 12
            hand_color = (0, 255, 100) if not hand_data.pinching else (255, 255, 0)
            
            # Draw hand glow
            for radius in [int(pulse * 1.5), int(pulse * 1.2), int(pulse)]:
                alpha = max(50, 150 - (radius - int(pulse)) * 10)
                glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*hand_color, alpha), (radius, radius), radius)
                self.screen.blit(glow_surface, (hand_data.x - radius, hand_data.y - radius), 
                               special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Main hand indicator
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse // 2))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse // 2), 2)
            
            # Status text
            status = f"Hand Tracking: {hand_data.hands_count} hands detected"
            status_color = (0, 255, 150)
        else:
            status = "Using mouse (no hand tracking)"
            status_color = (150, 150, 170)
        
        status_surface = self.font_small.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(current_width // 2, current_height - 60))
        
        # Status background
        status_bg = pygame.Rect(status_rect.x - 10, status_rect.y - 5, 
                              status_rect.width + 20, status_rect.height + 10)
        pygame.draw.rect(self.screen, (20, 20, 30, 180), status_bg, border_radius=5)
        self.screen.blit(status_surface, status_rect)
        
        # Enhanced instructions
        instructions = [
            "Hover over game cards and PINCH to select | Mouse click also works",
            "Hover over buttons for 1 sec or PINCH | ESC: Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = pygame.font.Font(None, 22).render(instruction, True, (120, 140, 160))
            text_rect = text_surface.get_rect(center=(current_width // 2, current_height - 100 + i * 25))
            
            # Instruction background
            inst_bg = pygame.Rect(text_rect.x - 8, text_rect.y - 3, 
                                text_rect.width + 16, text_rect.height + 6)
            pygame.draw.rect(self.screen, (15, 15, 25, 120), inst_bg, border_radius=3)
            self.screen.blit(text_surface, text_rect)
        
        # Draw version info
        version_text = "Developed and maintained by MCMMediaNetworks development team"
        version_surface = pygame.font.Font(None, 18).render(version_text, True, (80, 100, 120))
        version_rect = version_surface.get_rect(bottomright=(current_width - 20, current_height - 10))
        self.screen.blit(version_surface, version_rect)
    
    def run(self):
        print("Starting Enhanced Main Menu in fullscreen mode...")
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