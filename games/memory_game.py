# games/memory_game.py
"""
Memory Card Game using hand tracking
Match pairs of cards to win
Enhanced version with intro sequence and improved animations
"""

import pygame
import random
import math
import time
from .base_game import BaseGame
from core import *


class Card:
    """Individual memory card with enhanced animations"""
    def __init__(self, x, y, width, height, symbol, color):
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
        """Draw the card with enhanced animations"""
        # Don't draw if intro animation hasn't started yet
        if time_elapsed < self.intro_delay:
            return
            
        # Calculate card position with animations
        card_rect = self.rect.copy()
        
        # Intro slide-in effect
        if self.intro_animation < 1.0:
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
        
        # Create a surface for rotation effect
        card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        
        if show_face:
            self.draw_card_face(card_surface, pygame.Rect(0, 0, card_rect.width, card_rect.height), font)
        else:
            self.draw_card_back(card_surface, pygame.Rect(0, 0, card_rect.width, card_rect.height), time_elapsed)
        
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
    
    def draw_card_back(self, surface, rect, time_elapsed):
        """Draw the back of the card"""
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
    
    def draw_card_face(self, surface, rect, font):
        """Draw the face of the card with symbol"""
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
        
        # Game settings
        self.grid_cols = 4
        self.grid_rows = 3
        self.total_pairs = (self.grid_cols * self.grid_rows) // 2
        
        # Game states
        self.game_state = "intro_preview"  # intro_preview, countdown, playing, game_over
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
        
        # Visual settings
        self.card_width = 80
        self.card_height = 100
        self.card_spacing = 20
        
        # Symbols and colors for cards
        self.symbols = ['♠', '♥', '♦', '♣', '★', '●', '◆', '▲', '♪', '☀', '☽', '⚡']
        self.colors = [RED, BLUE, GREEN, PURPLE, CYAN, YELLOW, (255, 165, 0), (255, 20, 147)]
        
        # Game-specific UI
        self.new_game_button = AnimatedButton(
            WINDOW_WIDTH - 580, 20, 120, 50, "🎮 New Game", GREEN_DARK, GREEN
        )
        
        # Initialize game
        self.setup_game()
    
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
        self.game_state = "intro_preview"
        self.state_timer = time.time()
        
        # Create pairs of cards
        symbols_to_use = self.symbols[:self.total_pairs]
        colors_to_use = self.colors[:self.total_pairs]
        
        # Create card data (symbol, color pairs)
        card_data = []
        for i in range(self.total_pairs):
            symbol = symbols_to_use[i]
            color = colors_to_use[i]
            # Add two cards with same symbol and color (a pair)
            card_data.extend([(symbol, color), (symbol, color)])
        
        # Shuffle the cards
        random.shuffle(card_data)
        
        # Calculate grid layout
        total_width = self.grid_cols * self.card_width + (self.grid_cols - 1) * self.card_spacing
        total_height = self.grid_rows * self.card_height + (self.grid_rows - 1) * self.card_spacing
        
        start_x = (WINDOW_WIDTH - total_width) // 2
        start_y = 200  # Leave space for title and UI
        
        # Create Card objects
        for i, (symbol, color) in enumerate(card_data):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = start_x + col * (self.card_width + self.card_spacing)
            y = start_y + row * (self.card_height + self.card_spacing)
            
            card = Card(x, y, self.card_width, self.card_height, symbol, color)
            
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
                
                # Check for match
                card1, card2 = self.flipped_cards
                if card1.symbol == card2.symbol and card1.color == card2.color:
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
            elif event.key == pygame.K_SPACE and self.game_state == "intro_preview":
                # Skip intro
                self.game_state = "countdown"
                self.state_timer = time.time()
                for card in self.cards:
                    card.show_during_intro = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check new game button
            if self.new_game_button.is_clicked(event.pos, True):
                self.setup_game()
            else:
                # Check card clicks only during playing state
                if self.game_state == "playing":
                    card = self.get_card_at_position(event.pos[0], event.pos[1])
                    if card:
                        self.handle_card_click(card)
    
    def update_game_state(self):
        """Update the game state machine"""
        current_time = time.time()
        elapsed = current_time - self.state_timer
        
        if self.game_state == "intro_preview":
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
                    print(f"Pinch detected on card: {hovered_card.symbol}")
        
        self.last_pinch = hand_data.pinching
        
        # Update UI buttons
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        self.new_game_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Check for hand activation
        if self.new_game_button.is_hand_activated():
            self.setup_game()
            print("New game started by hand gesture!")
    
    def draw_game_state_overlay(self):
        """Draw overlays based on current game state"""
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2
        
        if self.game_state == "intro_preview":
            # Draw preview overlay
            elapsed = time.time() - self.state_timer
            remaining = max(0, self.preview_duration - elapsed)
            
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
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
            # Draw win overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 50, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Win text with animation
            pulse = math.sin(self.background_manager.time_elapsed * 3) * 0.3 + 1
            win_font_size = int(80 * pulse)
            win_font = pygame.font.Font(None, win_font_size)
            
            win_text = win_font.render("YOU WON!", True, YELLOW)
            win_rect = win_text.get_rect(center=(center_x, center_y - 80))
            self.screen.blit(win_text, win_rect)
            
            # Game stats
            game_time = time.time() - self.start_time
            minutes = int(game_time // 60)
            seconds = int(game_time % 60)
            
            stats_text = self.font_medium.render(f"Time: {minutes:02d}:{seconds:02d} | Moves: {self.moves}", True, WHITE)
            stats_rect = stats_text.get_rect(center=(center_x, center_y - 20))
            self.screen.blit(stats_text, stats_rect)
            
            # New game prompt
            prompt_text = self.font_medium.render("Press N for New Game", True, GREEN)
            prompt_rect = prompt_text.get_rect(center=(center_x, center_y + 40))
            self.screen.blit(prompt_text, prompt_rect)
    
    def draw_game(self):
        """Draw memory game specific elements"""
        # Draw title
        title_text = self.font_title.render("MEMORY GAME", True, WHITE)
        title_x = 250  # Positioned after logos
        title_y = 40
        self.screen.blit(title_text, (title_x, title_y))
        
        # Draw subtitle
        subtitle_text = self.font_small.render("Match pairs of cards", True, PURPLE)
        subtitle_x = title_x
        subtitle_y = title_y + 50
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # Draw cards
        for card in self.cards:
            card.draw(self.screen, self.font_large, self.background_manager.time_elapsed, self.game_state)
        
        # Draw hand indicator (only during playing)
        if self.game_state == "playing":
            hand_data = self.hand_tracker.hand_data
            if hand_data.active and hand_data.hands_count > 0:
                pulse = math.sin(self.background_manager.time_elapsed * 6) * 3 + 8
                hand_color = GREEN if not hand_data.pinching else YELLOW
                pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
                pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
        
        # Draw game stats (only during playing and game over)
        if self.game_state in ["playing", "game_over"]:
            stats_y = 600
            center_x = WINDOW_WIDTH // 2
            
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
        
        # Draw new game button
        self.new_game_button.draw(self.screen, self.font_small)
        
        # Instructions
        if self.game_state == "playing":
            instructions = [
                "Hover over cards and PINCH to flip them",
                "Match pairs of identical symbols",
                "Mouse click also works | N: New Game | ESC: Back to Menu"
            ]
            instruction_y = self.screen.get_height() - 80
            center_x = WINDOW_WIDTH // 2
            for i, instruction in enumerate(instructions):
                text = self.font_small.render(instruction, True, LIGHT_GRAY)
                text_rect = text.get_rect(center=(center_x, instruction_y + i * 25))
                self.screen.blit(text, text_rect)
        
        # Draw status during playing
        if self.game_state == "playing":
            hand_data = self.hand_tracker.hand_data
            center_x = WINDOW_WIDTH // 2
            
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
            status_rect = status_text.get_rect(center=(center_x, 680))
            self.screen.blit(status_text, status_rect)