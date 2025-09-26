# games/memory_game.py
"""
Memory Card Game using hand tracking
Match pairs of cards to win
Enhanced version with intro sequence and improved animations
Fixed fullscreen layout alignment issues
FIXED: Main Menu button functionality in win overlay
MODIFIED: Using PNG images for card fronts and backs
ENHANCED: Added start overlay before game begins
"""

import pygame
import random
import math
import time
import os
from .base_game import BaseGame
from core import *


class Card:
    """Individual memory card with enhanced animations and image support"""
    def __init__(self, x, y, width, height, symbol, color, front_image=None, back_image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.symbol = symbol
        self.color = color
        self.is_flipped = False
        self.is_matched = False
        self.flip_animation = 0.0  # 0 = face down, 1 = face up
        self.rotation_angle = 0.0  # For flip rotation effect
        self.hover_animation = 0.0
        self.match_animation = 0.0
        self.last_flip_time = 0
        self.intro_delay = 0  # For staggered intro animation
        self.intro_animation = 0.0
        self.show_during_intro = False
        
        # Image support
        self.front_image = front_image
        self.back_image = back_image
        self.scaled_front_image = None
        self.scaled_back_image = None
        
        # Scale images if provided
        if self.front_image:
            self.scaled_front_image = pygame.transform.scale(self.front_image, (width - 10, height - 10))
        if self.back_image:
            self.scaled_back_image = pygame.transform.scale(self.back_image, (width - 10, height - 10))
        
    def update_position(self, x, y):
        """Update card position - for layout recalculation"""
        self.rect.x = x
        self.rect.y = y
        
    def update(self, dt):
        """Update card animations"""
        # Intro animation (slide in effect)
        if self.intro_animation < 1.0:
            self.intro_animation = min(1.0, self.intro_animation + 2 * dt)
        
        # Flip animation with rotation
        target_flip = 1.0 if self.is_flipped else 0.0
        old_flip = self.flip_animation
        self.flip_animation += (target_flip - self.flip_animation) * 8 * dt
        
        # Calculate rotation angle based on flip animation
        if abs(self.flip_animation - old_flip) > 0.01:  # Only update if actively flipping
            # Smooth rotation: 0 -> 90 -> 180 degrees as flip goes 0 -> 0.5 -> 1
            if self.flip_animation <= 0.5:
                self.rotation_angle = self.flip_animation * 180  # 0 to 90 degrees
            else:
                self.rotation_angle = 90 + (self.flip_animation - 0.5) * 180  # 90 to 180 degrees
        
        # Hover animation
        self.hover_animation = max(0, self.hover_animation - 2 * dt)
        
        # Match animation
        if self.is_matched:
            self.match_animation = min(1.0, self.match_animation + 3 * dt)
    
    def set_hover(self, hovering):
        """Set hover state"""
        if hovering and not self.is_matched:
            self.hover_animation = 1.0
    
    def flip(self):
        """Flip the card"""
        if not self.is_matched and time.time() - self.last_flip_time > 0.3:
            self.is_flipped = not self.is_flipped
            self.last_flip_time = time.time()
            return True
        return False
    
    def set_intro_delay(self, delay):
        """Set delay for intro animation"""
        self.intro_delay = delay
        self.intro_animation = 0.0
    
    def draw(self, screen, font, time_elapsed, game_state="playing"):
        """Draw the card with enhanced animations and images"""
        # Don't draw if intro animation hasn't started yet
        if time_elapsed < self.intro_delay and game_state != "start_overlay":
            return
            
        # Calculate card position with animations
        card_rect = self.rect.copy()
        
        # Intro slide-in effect
        if self.intro_animation < 1.0 and game_state != "start_overlay":
            slide_offset = int((1 - self.intro_animation) * 100)
            card_rect.x += slide_offset
        
        # Hover effect - slight scale up
        if self.hover_animation > 0:
            scale_factor = 1 + self.hover_animation * 0.05
            center = self.rect.center
            scaled_width = int(self.rect.width * scale_factor)
            scaled_height = int(self.rect.height * scale_factor)
            card_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
            card_rect.center = center
        
        # Match effect - gentle pulse
        if self.is_matched:
            pulse = math.sin(time_elapsed * 3 + self.rect.x * 0.01) * 0.02 + 1
            center = card_rect.center
            pulsed_width = int(card_rect.width * pulse)
            pulsed_height = int(card_rect.height * pulse)
            card_rect = pygame.Rect(0, 0, pulsed_width, pulsed_height)
            card_rect.center = center
        
        # Draw card shadow
        shadow_rect = card_rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Determine what to show based on game state and flip animation
        show_face = False
        if game_state == "intro_preview" and self.show_during_intro:
            show_face = True
        elif game_state == "playing" and self.flip_animation > 0.5:
            show_face = True
        elif game_state == "start_overlay":
            show_face = False  # Always show back during start overlay
        
        # Create a surface for rotation effect
        card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        
        if show_face:
            self.draw_card_face_with_image(card_surface, pygame.Rect(0, 0, card_rect.width, card_rect.height), font)
        else:
            self.draw_card_back_with_image(card_surface, pygame.Rect(0, 0, card_rect.width, card_rect.height), time_elapsed)
        
        # Apply rotation if flipping
        if game_state == "playing" and abs(self.rotation_angle) > 1:
            # Calculate rotation scale (makes card appear to rotate in 3D)
            rotation_scale = abs(math.cos(math.radians(self.rotation_angle)))
            if rotation_scale < 0.1:
                rotation_scale = 0.1
                
            # Scale the surface horizontally to simulate 3D rotation
            scaled_width = int(card_rect.width * rotation_scale)
            if scaled_width > 0:
                rotated_surface = pygame.transform.scale(card_surface, (scaled_width, card_rect.height))
                rotated_rect = rotated_surface.get_rect(center=card_rect.center)
                screen.blit(rotated_surface, rotated_rect)
            else:
                # At 90 degrees, just draw a thin line
                pygame.draw.line(screen, LIGHT_GRAY, 
                               (card_rect.centerx, card_rect.top), 
                               (card_rect.centerx, card_rect.bottom), 2)
        else:
            screen.blit(card_surface, card_rect)
        
        # Draw glow effect for matched cards
        if self.is_matched and self.match_animation > 0.5:
            glow_surface = pygame.Surface((card_rect.width + 10, card_rect.height + 10))
            glow_alpha = int((math.sin(time_elapsed * 4) * 0.5 + 0.5) * 100)
            glow_surface.set_alpha(glow_alpha)
            pygame.draw.rect(glow_surface, self.color, (0, 0, card_rect.width + 10, card_rect.height + 10), border_radius=12)
            screen.blit(glow_surface, (card_rect.x - 5, card_rect.y - 5))
    
    def draw_card_back_with_image(self, surface, rect, time_elapsed):
        """Draw the back of the card using image or fallback pattern"""
        if self.scaled_back_image:
            # Draw background
            pygame.draw.rect(surface, WHITE, rect, border_radius=8)
            pygame.draw.rect(surface, DARK_GRAY, rect, 3, border_radius=8)
            
            # Center the back image
            image_rect = self.scaled_back_image.get_rect(center=rect.center)
            surface.blit(self.scaled_back_image, image_rect)
        else:
            # Fallback to original pattern
            # Main card background
            pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=8)
            pygame.draw.rect(surface, LIGHT_GRAY, rect, 2, border_radius=8)
            
            # Animated pattern on card back
            for i in range(3):
                for j in range(3):
                    dot_x = rect.x + 20 + j * 25
                    dot_y = rect.y + 20 + i * 25
                    
                    # Skip if outside card bounds
                    if dot_x > rect.right - 10 or dot_y > rect.bottom - 10:
                        continue
                    
                    # Animated dots
                    wave = math.sin(time_elapsed * 2 + i * j * 0.5) * 0.5 + 0.5
                    dot_size = int(3 + wave * 2)
                    dot_color = (int(100 + wave * 50), int(100 + wave * 50), int(120 + wave * 50))
                    pygame.draw.circle(surface, dot_color, (dot_x, dot_y), dot_size)
    
    def draw_card_face_with_image(self, surface, rect, font):
        """Draw the face of the card using image or fallback symbol"""
        if self.scaled_front_image:
            # Draw background
            pygame.draw.rect(surface, WHITE, rect, border_radius=8)
            pygame.draw.rect(surface, self.color, rect, 3, border_radius=8)
            
            # Center the front image
            image_rect = self.scaled_front_image.get_rect(center=rect.center)
            surface.blit(self.scaled_front_image, image_rect)
        else:
            # Fallback to original symbol drawing
            # Main card background
            pygame.draw.rect(surface, WHITE, rect, border_radius=8)
            pygame.draw.rect(surface, self.color, rect, 3, border_radius=8)
            
            # Draw symbol
            symbol_surface = font.render(self.symbol, True, self.color)
            symbol_rect = symbol_surface.get_rect(center=rect.center)
            surface.blit(symbol_surface, symbol_rect)


class MemoryGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Memory Game - Hand Tracking")
        
        # Load card images
        self.front_images = []
        self.back_images = []
        self.load_card_images()
        
        # Game settings
        self.grid_cols = 4
        self.grid_rows = 3
        self.total_pairs = (self.grid_cols * self.grid_rows) // 2
        
        # Game states - ENHANCED with start_overlay
        self.game_state = "start_overlay"  # start_overlay, intro_preview, countdown, playing, game_over
        self.state_timer = 0
        self.preview_duration = 3.0  # Show cards for 3 seconds
        self.countdown_duration = 3.0  # 3 second countdown
        
        # Game data
        self.cards = []
        self.flipped_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.game_over = False
        self.game_won = False
        self.flip_timer = 0
        self.checking_match = False
        self.last_pinch = False
        self.start_time = time.time()
        
        # FIXED: Add proper return flag
        self.should_return_to_menu = False
        
        # Visual settings
        self.card_width = 160
        self.card_height = 180
        self.card_spacing = 60
        
        # Symbols and colors for cards (fallback)
        self.symbols = ['♠', '♥', '♦', '♣', '★', '●', '◆', '▲', '♪', '☀', '☽', '⚡']
        self.colors = [RED, BLUE, GREEN, PURPLE, CYAN, YELLOW, (255, 165, 0), (255, 20, 147)]
        
        # Game-specific UI - will be positioned dynamically
        self.create_game_buttons()
        
        # WIN OVERLAY BUTTONS - NEW ADDITION
        self.win_new_game_button = None
        self.win_main_menu_button = None
        self.create_win_overlay_buttons()
        
        # START OVERLAY BUTTON - NEW ADDITION
        self.start_game_button = None
        self.create_start_overlay_button()
        
        # Initialize game
        self.setup_game()
    
    def load_card_images(self):
        """Load card images from assets folder"""
        try:
            # Define base path for assets
            assets_path = "assets"
            
            # Load front images (Adidas designs)
            front_path = os.path.join(assets_path, "cards", "front")
            front_image_files = [
                "adidas_adizero.png",
                "adidas_bywx.png", 
                "adidas_crazy8.png",
                "adidas_drose.png",
                "adidas_own.png",
                "adidas_ultraboost.png"
            ]
            
            for image_file in front_image_files:
                image_path = os.path.join(front_path, image_file)
                if os.path.exists(image_path):
                    try:
                        image = pygame.image.load(image_path).convert_alpha()
                        self.front_images.append(image)
                        print(f"Loaded front image: {image_file}")
                    except pygame.error as e:
                        print(f"Error loading front image {image_file}: {e}")
            
            # Load back images
            back_path = os.path.join(assets_path, "cards", "back")
            back_image_file = "3-stripes.png"
            back_image_path = os.path.join(back_path, back_image_file)
            
            if os.path.exists(back_image_path):
                try:
                    back_image = pygame.image.load(back_image_path).convert_alpha()
                    self.back_images.append(back_image)
                    print(f"Loaded back image: {back_image_file}")
                except pygame.error as e:
                    print(f"Error loading back image {back_image_file}: {e}")
                    
        except Exception as e:
            print(f"Error loading card images: {e}")
            print("Using fallback symbols and patterns")
        
        print(f"Loaded {len(self.front_images)} front images and {len(self.back_images)} back images")
    
    def create_game_buttons(self):
        """Create game-specific buttons with dynamic positioning"""
        current_width, current_height = self.get_current_screen_size()
        
        self.new_game_button = AnimatedButton(
            current_width - 200, 20, 120, 50, "New Game", GREEN_DARK, GREEN
        )
    
    def create_win_overlay_buttons(self):
        """Create buttons for win overlay"""
        current_width, current_height = self.get_current_screen_size()
        center_x = current_width // 2
        center_y = current_height // 2
        
        # Only New Game button - no Main Menu button
        self.win_new_game_button = AnimatedButton(
            center_x - 70, center_y + 80, 140, 50, "New Game", GREEN_DARK, GREEN
        )
        
        # Remove Main Menu button completely
        self.win_main_menu_button = None
    
    def create_start_overlay_button(self):
        """Create button for start overlay - NEW FUNCTION"""
        current_width, current_height = self.get_current_screen_size()
        center_x = current_width // 2
        center_y = current_height // 2
        
        self.start_game_button = AnimatedButton(
            center_x - 80, center_y + 30, 160, 60, "START GAME", BLUE, CYAN
        )
    
    def recalculate_game_layout(self):
        """Recalculate game-specific layout when screen size changes"""
        print("Recalculating Memory Game layout...")
        self.create_game_buttons()
        self.create_win_overlay_buttons()
        self.create_start_overlay_button()  # NEW: Recalculate start overlay button
        self.calculate_card_layout()
        
        # Update existing cards with new positions
        if self.cards:
            self.recalculate_card_positions()
    
    def calculate_card_layout(self):
        """Calculate card layout based on current screen size"""
        current_width, current_height = self.get_current_screen_size()
        
        # Calculate grid layout
        total_width = self.grid_cols * self.card_width + (self.grid_cols - 1) * self.card_spacing
        total_height = self.grid_rows * self.card_height + (self.grid_rows - 1) * self.card_spacing
        
        self.start_x = (current_width - total_width) // 2  # Fixed: use current screen width
        self.start_y = 200  # Leave space for title and UI
        
        print(f"Card layout: {total_width}x{total_height} at ({self.start_x}, {self.start_y})")
    
    def recalculate_card_positions(self):
        """Update existing card positions after screen size change"""
        for i, card in enumerate(self.cards):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = self.start_x + col * (self.card_width + self.card_spacing)
            y = self.start_y + row * (self.card_height + self.card_spacing)
            
            card.update_position(x, y)
    
    def get_game_info(self):
        return {
            'name': 'Memory Game',
            'description': 'Match pairs of cards to win',
            'preview_color': PURPLE
        }
    
    def setup_game(self):
        """Initialize a new game"""
        self.cards = []
        self.flipped_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.game_over = False
        self.game_won = False
        self.flip_timer = 0
        self.checking_match = False
        self.game_state = "start_overlay"  # MODIFIED: Start with start overlay
        self.state_timer = time.time()
        
        # Reset return flag when starting new game
        self.should_return_to_menu = False
        
        # Reset button states to prevent activation loops
        if self.win_new_game_button:
            if hasattr(self.win_new_game_button, 'reset_activation'):
                self.win_new_game_button.reset_activation()
        
        if self.start_game_button:
            if hasattr(self.start_game_button, 'reset_activation'):
                self.start_game_button.reset_activation()
        
        # Calculate layout based on current screen size
        self.calculate_card_layout()
        
        # Create pairs of cards with images
        self.create_card_pairs()
    
    def create_card_pairs(self):
        """Create card pairs using images or fallback to symbols"""
        card_data = []
        
        if len(self.front_images) >= self.total_pairs:
            # Use images for cards
            for i in range(self.total_pairs):
                front_image = self.front_images[i]
                back_image = self.back_images[0] if self.back_images else None
                color = self.colors[i % len(self.colors)]
                
                # Create two identical cards (a pair)
                card_data.extend([
                    ("image", color, front_image, back_image),
                    ("image", color, front_image, back_image)
                ])
        else:
            # Fallback to symbols if not enough images
            symbols_to_use = self.symbols[:self.total_pairs]
            colors_to_use = self.colors[:self.total_pairs]
            
            for i in range(self.total_pairs):
                symbol = symbols_to_use[i]
                color = colors_to_use[i]
                back_image = self.back_images[0] if self.back_images else None
                
                # Create two identical cards (a pair)
                card_data.extend([
                    (symbol, color, None, back_image),
                    (symbol, color, None, back_image)
                ])
        
        # Shuffle the cards
        random.shuffle(card_data)
        
        # Create Card objects using calculated layout
        for i, (symbol, color, front_image, back_image) in enumerate(card_data):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = self.start_x + col * (self.card_width + self.card_spacing)
            y = self.start_y + row * (self.card_height + self.card_spacing)
            
            card = Card(x, y, self.card_width, self.card_height, symbol, color, front_image, back_image)
            
            # Set intro animation delay for staggered effect
            delay = (row * self.grid_cols + col) * 0.1
            card.set_intro_delay(delay)
            card.show_during_intro = True  # Show face during intro
            
            self.cards.append(card)
    
    def get_card_at_position(self, x, y):
        """Get the card at the given screen position"""
        for card in self.cards:
            if card.rect.collidepoint(x, y) and not card.is_matched:
                return card
        return None
    
    def handle_card_click(self, card):
        """Handle clicking/pinching a card"""
        if (self.game_state != "playing" or self.checking_match or 
            card.is_matched or card in self.flipped_cards):
            return
        
        # Flip the card
        if card.flip():
            self.flipped_cards.append(card)
            
            # Check if we have two flipped cards
            if len(self.flipped_cards) == 2:
                self.moves += 1
                self.checking_match = True
                self.flip_timer = time.time()
                
                # Check for match (compare images or symbols)
                card1, card2 = self.flipped_cards
                cards_match = False
                
                if card1.front_image and card2.front_image:
                    # Compare images (same object reference means same image)
                    cards_match = card1.front_image is card2.front_image
                else:
                    # Compare symbols and colors
                    cards_match = (card1.symbol == card2.symbol and card1.color == card2.color)
                
                if cards_match:
                    # Match found
                    card1.is_matched = True
                    card2.is_matched = True
                    self.matched_pairs += 1
                    self.flipped_cards = []
                    self.checking_match = False
                    
                    # Check win condition
                    if self.matched_pairs == self.total_pairs:
                        self.game_won = True
                        self.game_state = "game_over"
                        print("Game Won!")
    
    def handle_game_events(self, event):
        """Handle memory game specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                self.setup_game()
            elif event.key == pygame.K_SPACE:
                if self.game_state == "start_overlay":
                    # Start the game from start overlay
                    self.game_state = "intro_preview"
                    self.state_timer = time.time()
                elif self.game_state == "intro_preview":
                    # Skip intro
                    self.game_state = "countdown"
                    self.state_timer = time.time()
                    for card in self.cards:
                        card.show_during_intro = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle start overlay button click - NEW
            if self.game_state == "start_overlay":
                mouse_pos = event.pos
                if (self.start_game_button and 
                    self.start_game_button.rect.collidepoint(mouse_pos)):
                    print("Start Game button clicked!")
                    self.game_state = "intro_preview"
                    self.state_timer = time.time()
                    return None
            
            # Simplified win overlay button handling - only New Game button
            elif self.game_state == "game_over" and self.game_won:
                mouse_pos = event.pos
                print(f"Win overlay active, mouse clicked at: {mouse_pos}")
                
                # Check New Game button only
                if (self.win_new_game_button and 
                    self.win_new_game_button.rect.collidepoint(mouse_pos)):
                    print("New Game button clicked!")
                    self.setup_game()
                    return None
            
            # Check regular game buttons (only if not in win overlay or start overlay)
            elif self.game_state not in ["start_overlay", "game_over"]:
                if self.new_game_button and self.new_game_button.is_clicked(event.pos, True):
                    self.setup_game()
            
            # Check card clicks only during playing state
            if self.game_state == "playing":
                card = self.get_card_at_position(event.pos[0], event.pos[1])
                if card:
                    self.handle_card_click(card)
        
        return None
    
    def update_game_state(self):
        """Update the game state machine"""
        current_time = time.time()
        elapsed = current_time - self.state_timer
        
        # NEW: start_overlay state - wait for user input
        if self.game_state == "start_overlay":
            # Stay in start overlay until user clicks start button or presses space
            pass
        
        elif self.game_state == "intro_preview":
            # Show all cards for preview_duration
            if elapsed >= self.preview_duration:
                self.game_state = "countdown"
                self.state_timer = current_time
                # Hide card faces
                for card in self.cards:
                    card.show_during_intro = False
        
        elif self.game_state == "countdown":
            # Countdown before game starts
            if elapsed >= self.countdown_duration:
                self.game_state = "playing"
                self.start_time = current_time  # Start the game timer
    
    def update_game(self):
        """Update memory game state"""
        dt = 1/60  # Assuming 60 FPS
        
        # Update game state machine
        self.update_game_state()
        
        # Update all cards
        for card in self.cards:
            card.update(dt)
        
        # Handle match checking timeout (only during playing state)
        if (self.game_state == "playing" and self.checking_match and 
            time.time() - self.flip_timer > 1.0):
            # No match - flip cards back
            for card in self.flipped_cards:
                card.flip()
            self.flipped_cards = []
            self.checking_match = False
        
        # Hand tracking
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if no hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Update card hover states (only during playing)
        if self.game_state == "playing":
            hovered_card = self.get_card_at_position(hand_data.x, hand_data.y)
            for card in self.cards:
                card.set_hover(card == hovered_card)
            
            # Handle pinch gesture
            if hand_data.pinching and not self.last_pinch:
                if hovered_card:
                    self.handle_card_click(hovered_card)
                    print(f"Pinch detected on card")
        
        self.last_pinch = hand_data.pinching
        
        # Update UI buttons based on game state
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        
        # Update start overlay button - NEW
        if self.game_state == "start_overlay":
            if self.start_game_button:
                self.start_game_button.update(mouse_pos, hand_pos, hand_data.pinching)
                
                # Check for hand gesture activation
                if self.start_game_button.is_hand_activated():
                    print("Game started from start overlay by hand gesture!")
                    self.game_state = "intro_preview"
                    self.state_timer = time.time()
                    return None
                
                # Add pinch detection for start button
                if hand_data.pinching and not self.last_pinch:
                    if self.start_game_button.rect.collidepoint(hand_data.x, hand_data.y):
                        print("Start Game button activated by pinch!")
                        self.game_state = "intro_preview"
                        self.state_timer = time.time()
                        return None
        
        # Update regular game buttons (not during start overlay or win overlay)
        elif self.game_state not in ["start_overlay", "game_over"]:
            self.new_game_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Simplified win overlay button update - only New Game button
        elif self.game_state == "game_over" and self.game_won:
            if self.win_new_game_button:
                self.win_new_game_button.update(mouse_pos, hand_pos, hand_data.pinching)
                
                # Check for hand gesture activation
                if self.win_new_game_button.is_hand_activated():
                    print("New Game started from win overlay by hand gesture!")
                    self.setup_game()
                    return None
            
            # Add pinch detection for win overlay New Game button
            if hand_data.pinching and not self.last_pinch:
                if (self.win_new_game_button and 
                    self.win_new_game_button.rect.collidepoint(hand_data.x, hand_data.y)):
                    print("New Game button activated by pinch!")
                    self.setup_game()
                    return None
        
        # Check for hand activation on regular buttons (not during overlays)
        if (self.game_state not in ["start_overlay", "game_over"] and 
            self.new_game_button.is_hand_activated()):
            self.setup_game()
            print("New game started by hand gesture!")
        
        return None
    
    def draw_start_overlay(self):
        """Draw the start overlay - NEW FUNCTION"""
        current_width, current_height = self.get_current_screen_size()
        center_x = current_width // 2
        center_y = current_height // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((current_width, current_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 60))  # Dark blue background
        self.screen.blit(overlay, (0, 0))
        
        # Animated background effects
        time_elapsed = self.background_manager.time_elapsed
        for i in range(15):
            circle_x = (center_x - 400 + i * 60) + math.sin(time_elapsed * 1.5 + i * 0.3) * 30
            circle_y = (center_y - 250) + math.cos(time_elapsed * 2 + i * 0.4) * 40
            circle_size = int(5 + math.sin(time_elapsed * 3 + i) * 3)
            alpha = int((math.sin(time_elapsed * 2 + i * 0.2) * 0.5 + 0.5) * 150)
            
            # Create a surface for the circle with alpha
            circle_surface = pygame.Surface((circle_size * 2, circle_size * 2))
            circle_surface.set_alpha(alpha)
            pygame.draw.circle(circle_surface, CYAN, (circle_size, circle_size), circle_size)
            self.screen.blit(circle_surface, (circle_x - circle_size, circle_y - circle_size))
        
        # Game title (static, no animation)
        title_font = pygame.font.Font(None, 100)
        
        # Title shadow
        title_shadow = title_font.render("MEMORY GAME", True, (50, 50, 50))
        shadow_rect = title_shadow.get_rect(center=(center_x + 3, center_y - 147))
        self.screen.blit(title_shadow, shadow_rect)
        
        # Main title
        title_text = title_font.render("MEMORY GAME", True, YELLOW)
        title_rect = title_text.get_rect(center=(center_x, center_y - 170))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_large.render("Match pairs of cards to win!", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(center_x, center_y - 100))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Game features
        features = [
            "Hand tracking or mouse control",
            "12 cards to match",
        ]
        
        feature_start_y = center_y - 50
        for i, feature in enumerate(features):
            feature_text = self.font_medium.render(feature, True, LIGHT_GRAY)
            feature_rect = feature_text.get_rect(center=(center_x, feature_start_y + i * 30))
            self.screen.blit(feature_text, feature_rect)
        
        # Draw start button
        if self.start_game_button:
            self.start_game_button.draw(self.screen, self.font_medium)
        
        # Instructions
        instructions = [
            "Click START GAME or press SPACE to begin",
            "Use mouse or hand gestures to play"
        ]
        
        instruction_start_y = center_y + 120
        for i, instruction in enumerate(instructions):
            text_color = GREEN if i == 0 else LIGHT_GRAY
            instruction_text = self.font_small.render(instruction, True, text_color)
            instruction_rect = instruction_text.get_rect(center=(center_x, instruction_start_y + i * 25))
            self.screen.blit(instruction_text, instruction_rect)
        
        # Hand tracking status
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            status = f"Hand Tracking Active: {hand_data.hands_count} hands detected"
            status_color = GREEN
        else:
            status = "Mouse mode - Hand tracking not available"
            status_color = LIGHT_GRAY
        
        status_text = self.font_small.render(status, True, status_color)
        status_rect = status_text.get_rect(center=(center_x, center_y + 200))
        self.screen.blit(status_text, status_rect)
    
    def draw_game_state_overlay(self):
        """Draw overlays based on current game state"""
        current_width, current_height = self.get_current_screen_size()
        center_x = current_width // 2
        center_y = current_height // 2
        
        if self.game_state == "start_overlay":
            # Draw start overlay - NEW
            self.draw_start_overlay()
        
        elif self.game_state == "intro_preview":
            # Draw preview overlay
            elapsed = time.time() - self.state_timer
            remaining = max(0, self.preview_duration - elapsed)
            
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Preview text
            preview_text = self.font_large.render("MEMORIZE THE CARDS!", True, WHITE)
            preview_rect = preview_text.get_rect(center=(center_x, center_y - 50))
            self.screen.blit(preview_text, preview_rect)
            
            # Timer
            timer_text = self.font_medium.render(f"Starting in: {int(remaining) + 1}", True, YELLOW)
            timer_rect = timer_text.get_rect(center=(center_x, center_y))
            self.screen.blit(timer_text, timer_rect)
            
            # Skip instruction
            skip_text = self.font_small.render("Press SPACE to skip", True, LIGHT_GRAY)
            skip_rect = skip_text.get_rect(center=(center_x, center_y + 50))
            self.screen.blit(skip_text, skip_rect)
        
        elif self.game_state == "countdown":
            # Draw countdown
            elapsed = time.time() - self.state_timer
            remaining = max(0, self.countdown_duration - elapsed)
            countdown_num = int(remaining) + 1
            
            if countdown_num > 0:
                # Pulsing countdown number
                pulse = math.sin(elapsed * 10) * 0.2 + 1
                size = int(120 * pulse)
                
                # Create font for countdown
                countdown_font = pygame.font.Font(None, size)
                countdown_text = countdown_font.render(str(countdown_num), True, RED)
                countdown_rect = countdown_text.get_rect(center=(center_x, center_y))
                
                # Draw glow effect
                glow_surface = pygame.Surface((countdown_text.get_width() + 20, countdown_text.get_height() + 20))
                glow_surface.set_alpha(100)
                glow_text = countdown_font.render(str(countdown_num), True, WHITE)
                glow_rect = glow_text.get_rect(center=(glow_surface.get_width()//2, glow_surface.get_height()//2))
                glow_surface.blit(glow_text, glow_rect)
                
                glow_pos = (countdown_rect.x - 10, countdown_rect.y - 10)
                self.screen.blit(glow_surface, glow_pos)
                self.screen.blit(countdown_text, countdown_rect)
        
        elif self.game_state == "game_over" and self.game_won:
            # Draw win overlay with enhanced styling
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(220)
            overlay.fill((0, 40, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Animated background effects
            for i in range(10):
                star_x = (center_x - 300 + i * 60) + math.sin(self.background_manager.time_elapsed * 2 + i) * 20
                star_y = (center_y - 200) + math.cos(self.background_manager.time_elapsed * 3 + i * 0.5) * 30
                star_size = int(3 + math.sin(self.background_manager.time_elapsed * 4 + i) * 2)
                pygame.draw.circle(self.screen, YELLOW, (int(star_x), int(star_y)), star_size)
            
            # Win text with animation
            pulse = math.sin(self.background_manager.time_elapsed * 3) * 0.3 + 1
            win_font_size = int(80 * pulse)
            win_font = pygame.font.Font(None, win_font_size)
            
            # Gradient text effect
            win_text = win_font.render("YOU WON!", True, YELLOW)
            win_rect = win_text.get_rect(center=(center_x, center_y - 120))
            
            # Draw text shadow
            shadow_text = win_font.render("YOU WON!", True, (100, 100, 0))
            shadow_rect = shadow_text.get_rect(center=(center_x + 3, center_y - 117))
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(win_text, win_rect)
            
            # Celebration message
            celebration_messages = ["Excellent Memory!", "Well Done!", "Perfect Match!", "Outstanding!"]
            message_index = int(self.background_manager.time_elapsed) % len(celebration_messages)
            celebration_text = self.font_medium.render(celebration_messages[message_index], True, CYAN)
            celebration_rect = celebration_text.get_rect(center=(center_x, center_y - 80))
            self.screen.blit(celebration_text, celebration_rect)
            
            # Game stats with better formatting
            game_time = time.time() - self.start_time
            minutes = int(game_time // 60)
            seconds = int(game_time % 60)
            
            # Stats background
            stats_bg = pygame.Surface((400, 60))
            stats_bg.set_alpha(150)
            stats_bg.fill(DARK_GRAY)
            stats_bg_rect = stats_bg.get_rect(center=(center_x, center_y - 20))
            self.screen.blit(stats_bg, stats_bg_rect)
            
            stats_text = self.font_medium.render(f"Time: {minutes:02d}:{seconds:02d}  |  Moves: {self.moves}", True, WHITE)
            stats_rect = stats_text.get_rect(center=(center_x, center_y - 20))
            self.screen.blit(stats_text, stats_rect)
            
            # Performance rating
            if self.moves <= self.total_pairs + 2:
                rating = "PERFECT!"
                rating_color = YELLOW
            elif self.moves <= self.total_pairs + 5:
                rating = "GREAT!"
                rating_color = GREEN
            else:
                rating = "GOOD!"
                rating_color = BLUE
            
            rating_text = self.font_medium.render(rating, True, rating_color)
            rating_rect = rating_text.get_rect(center=(center_x, center_y + 20))
            self.screen.blit(rating_text, rating_rect)
            
            # Draw win overlay button - only New Game
            if self.win_new_game_button:
                self.win_new_game_button.draw(self.screen, self.font_small)
            
            # Simplified button instructions
            hand_data = self.hand_tracker.hand_data
            if hand_data.active and hand_data.hands_count > 0:
                button_instruction = "Hover and PINCH to select | Mouse click also works"
                instruction_color = GREEN
                
                # Additional hand status
                hand_status = f"Hand Tracking: {hand_data.hands_count} hands detected"
                status_text = self.font_small.render(hand_status, True, GREEN)
                status_rect = status_text.get_rect(center=(center_x, center_y + 170))
                self.screen.blit(status_text, status_rect)
            else:
                button_instruction = "Click button to select (Mouse mode)"
                instruction_color = LIGHT_GRAY
                
                # Hand tracking offline status
                hand_status = "Hand tracking not available - using mouse"
                status_text = self.font_small.render(hand_status, True, LIGHT_GRAY)
                status_rect = status_text.get_rect(center=(center_x, center_y + 170))
                self.screen.blit(status_text, status_rect)
            
            instruction_text = self.font_small.render(button_instruction, True, instruction_color)
            instruction_rect = instruction_text.get_rect(center=(center_x, center_y + 150))
            self.screen.blit(instruction_text, instruction_rect)
    
    def draw_game(self):
        """Draw memory game specific elements"""
        current_width, current_height = self.get_current_screen_size()
        
        # Draw cards (except during start overlay)
        if self.game_state != "start_overlay":
            for card in self.cards:
                card.draw(self.screen, self.font_large, self.background_manager.time_elapsed, self.game_state)
        
        # Draw hand indicator (during playing and game over states, and start overlay) - MODIFIED
        if self.game_state in ["playing", "game_over", "start_overlay"]:
            hand_data = self.hand_tracker.hand_data
            if hand_data.active and hand_data.hands_count > 0:
                pulse = math.sin(self.background_manager.time_elapsed * 6) * 3 + 8
                hand_color = GREEN if not hand_data.pinching else YELLOW
                
                # Enhanced visibility during overlays
                if self.game_state in ["game_over", "start_overlay"] and self.game_won or self.game_state == "start_overlay":
                    # Larger and brighter indicator for overlays
                    pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse + 2))
                    pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse + 2), 3)
                    # Add inner glow
                    glow_surface = pygame.Surface((int(pulse * 2 + 20), int(pulse * 2 + 20)))
                    glow_surface.set_alpha(80)
                    pygame.draw.circle(glow_surface, hand_color, 
                                     (int(pulse + 10), int(pulse + 10)), int(pulse + 5))
                    self.screen.blit(glow_surface, (hand_data.x - int(pulse + 10), hand_data.y - int(pulse + 10)))
                else:
                    # Normal indicator for playing state
                    pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
                    pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
        
        # Draw game stats (only during playing and game over) - Fixed: use dynamic screen size
        if self.game_state in ["playing", "game_over"]:
            stats_y = 1000
            center_x = current_width // 2
            
            # Moves counter
            moves_text = self.font_medium.render(f"Moves: {self.moves}", True, WHITE)
            moves_rect = moves_text.get_rect(center=(center_x - 120, stats_y))
            self.screen.blit(moves_text, moves_rect)
            
            # Pairs found
            pairs_text = self.font_medium.render(f"Pairs: {self.matched_pairs}/{self.total_pairs}", True, WHITE)
            pairs_rect = pairs_text.get_rect(center=(center_x + 120, stats_y))
            self.screen.blit(pairs_text, pairs_rect)
            
            # Timer (only show during playing)
            if self.game_state == "playing":
                elapsed_time = time.time() - self.start_time
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)
                time_text = self.font_medium.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
                time_rect = time_text.get_rect(center=(center_x, stats_y + 40))
                self.screen.blit(time_text, time_rect)
        
        # Draw game state overlay
        self.draw_game_state_overlay()
        
        # Draw new game button (only when not in game over state or start overlay) - MODIFIED
        if self.game_state not in ["game_over", "start_overlay"]:
            self.new_game_button.draw(self.screen, self.font_small)
        
        # Instructions - Fixed: use dynamic screen size
        if self.game_state == "playing":
            instructions = [
                "Developed and Maintained by GVI PT. Maxima Cipta Miliardatha development team"
            ]
            instruction_y = 50
            center_x = current_width // 2
            for i, instruction in enumerate(instructions):
                text = self.font_small.render(instruction, True, WHITE)
                text_rect = text.get_rect(center=(center_x, instruction_y + i * 25))
                self.screen.blit(text, text_rect)
            
            # Hand tracking status for playing mode
            hand_data = self.hand_tracker.hand_data
            center_x = current_width // 2
            
            if self.checking_match:
                status = "Checking match..."
                status_color = YELLOW
            else:
                if hand_data.active and hand_data.hands_count > 0:
                    status = f"Hand Tracking: {hand_data.hands_count} hands detected"
                    status_color = GREEN
                else:
                    status = "Using mouse (no hand tracking)"
                    status_color = LIGHT_GRAY
            
            status_text = self.font_medium.render(status, True, status_color)
            status_rect = status_text.get_rect(center=(center_x, 900))
            self.screen.blit(status_text, status_rect)
        
        # ALWAYS draw hand indicator on top of everything (including overlays) - ENHANCED
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            pulse = math.sin(self.background_manager.time_elapsed * 6) * 3 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            
            # Enhanced visibility for overlays
            if self.game_state in ["game_over", "start_overlay"]:
                # Extra bright and large indicator
                glow_size = int(pulse * 2 + 10)
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2))
                glow_surface.set_alpha(60)
                pygame.draw.circle(glow_surface, hand_color, (glow_size, glow_size), glow_size)
                self.screen.blit(glow_surface, (hand_data.x - glow_size, hand_data.y - glow_size))
                
                # Main indicator (larger)
                main_size = int(pulse + 4)
                pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), main_size)
                pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), main_size, 4)
                
                # Inner highlight
                pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), max(2, main_size - 6))
            else:
                # Normal indicator for other states
                pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
                pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)