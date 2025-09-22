# games/memory_game.py
"""
Memory Card Game using hand tracking
Match pairs of cards to win
"""

import pygame
import random
import math
import time
from .base_game import BaseGame
from core import *


class Card:
    """Individual memory card"""
    def __init__(self, x, y, width, height, symbol, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.symbol = symbol
        self.color = color
        self.is_flipped = False
        self.is_matched = False
        self.flip_animation = 0.0  # 0 = face down, 1 = face up
        self.hover_animation = 0.0
        self.match_animation = 0.0
        self.last_flip_time = 0
        
    def update(self, dt):
        """Update card animations"""
        # Flip animation
        target_flip = 1.0 if self.is_flipped else 0.0
        self.flip_animation += (target_flip - self.flip_animation) * 8 * dt
        
        # Hover animation (will be set externally)
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
    
    def draw(self, screen, font, time_elapsed):
        """Draw the card with animations"""
        # Calculate card position with animations
        card_rect = self.rect.copy()
        
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
        
        # Determine card appearance based on flip animation
        if self.flip_animation < 0.5:
            # Face down - show card back
            self.draw_card_back(screen, card_rect, time_elapsed)
        else:
            # Face up - show symbol
            self.draw_card_face(screen, card_rect, font)
        
        # Draw glow effect for matched cards
        if self.is_matched and self.match_animation > 0.5:
            glow_surface = pygame.Surface((card_rect.width + 10, card_rect.height + 10))
            glow_alpha = int((math.sin(time_elapsed * 4) * 0.5 + 0.5) * 100)
            glow_surface.set_alpha(glow_alpha)
            pygame.draw.rect(glow_surface, self.color, (0, 0, card_rect.width + 10, card_rect.height + 10), border_radius=12)
            screen.blit(glow_surface, (card_rect.x - 5, card_rect.y - 5))
    
    def draw_card_back(self, screen, rect, time_elapsed):
        """Draw the back of the card"""
        # Main card background
        pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=8)
        pygame.draw.rect(screen, LIGHT_GRAY, rect, 2, border_radius=8)
        
        # Animated pattern on card back
        center_x, center_y = rect.center
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
                pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_size)
    
    def draw_card_face(self, screen, rect, font):
        """Draw the face of the card with symbol"""
        # Main card background
        pygame.draw.rect(screen, WHITE, rect, border_radius=8)
        pygame.draw.rect(screen, self.color, rect, 3, border_radius=8)
        
        # Draw symbol
        symbol_surface = font.render(self.symbol, True, self.color)
        symbol_rect = symbol_surface.get_rect(center=rect.center)
        screen.blit(symbol_surface, symbol_rect)


class MemoryGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Memory Game - Hand Tracking")
        
        # Game settings
        self.grid_cols = 4
        self.grid_rows = 3
        self.total_pairs = (self.grid_cols * self.grid_rows) // 2
        
        # Game state
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
        self.start_time = time.time()
        
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
            self.cards.append(card)
    
    def get_card_at_position(self, x, y):
        """Get the card at the given screen position"""
        for card in self.cards:
            if card.rect.collidepoint(x, y) and not card.is_matched:
                return card
        return None
    
    def handle_card_click(self, card):
        """Handle clicking/pinching a card"""
        if self.checking_match or card.is_matched or card in self.flipped_cards:
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
                        self.game_over = True
                        print("Game Won!")
    
    def handle_game_events(self, event):
        """Handle memory game specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                self.setup_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check new game button
            if self.new_game_button.is_clicked(event.pos, True):
                self.setup_game()
            else:
                # Check card clicks
                card = self.get_card_at_position(event.pos[0], event.pos[1])
                if card:
                    self.handle_card_click(card)
    
    def update_game(self):
        """Update memory game state"""
        dt = 1/60  # Assuming 60 FPS
        
        # Update all cards
        for card in self.cards:
            card.update(dt)
        
        # Handle match checking timeout
        if self.checking_match and time.time() - self.flip_timer > 1.0:
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
        
        # Update card hover states
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
            card.draw(self.screen, self.font_large, self.background_manager.time_elapsed)
        
        # Draw hand indicator
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            pulse = math.sin(self.background_manager.time_elapsed * 6) * 3 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
        
        # Draw game stats
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
        
        # Timer
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = self.font_medium.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=(center_x, stats_y + 40))
        self.screen.blit(time_text, time_rect)
        
        # Game status
        if self.game_won:
            status = "Congratulations! You won!"
            status_color = GREEN
        elif self.checking_match:
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
        status_rect = status_text.get_rect(center=(center_x, stats_y + 80))
        self.screen.blit(status_text, status_rect)
        
        # Draw new game button
        self.new_game_button.draw(self.screen, self.font_small)
        
        # Instructions
        instructions = [
            "Hover over cards and PINCH to flip them",
            "Match pairs of identical symbols",
            "Mouse click also works | N: New Game | ESC: Back to Menu"
        ]
        instruction_y = self.screen.get_height() - 80
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(center_x, instruction_y + i * 25))
            self.screen.blit(text, text_rect)