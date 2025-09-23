# games/tic_tac_toe.py
"""
Tic Tac Toe game refactored to use BaseGame architecture
Fixed fullscreen layout alignment issues
"""

import pygame
import math
from .base_game import BaseGame
from core import *


class TicTacToeGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Enhanced Hand Tracking Tic Tac Toe")
        
        # Game state
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_line = None
        
        # Visual effects
        self.cell_animations = [[0 for _ in range(3)] for _ in range(3)]
        self.last_pinch = False
        
        # Dynamic grid positioning - will be calculated based on screen size
        self.calculate_grid_layout()
        
        # Add reset button specific to this game
        self.create_game_buttons()
    
    def calculate_grid_layout(self):
        """Calculate grid layout based on current screen size"""
        current_width, current_height = self.get_current_screen_size()
        
        # Center the grid on the screen
        self.grid_size = 450  # Keep grid size constant
        self.cell_size = self.grid_size // 3
        self.grid_offset_x = (current_width - self.grid_size) // 2
        self.grid_offset_y = 180  # Fixed vertical offset from top
        
        print(f"Grid layout: {self.grid_size}x{self.grid_size} at ({self.grid_offset_x}, {self.grid_offset_y})")
    
    def create_game_buttons(self):
        """Create game-specific buttons with dynamic positioning"""
        current_width, current_height = self.get_current_screen_size()
        
        self.reset_button = AnimatedButton(
            current_width - 580, 20, 120, 50, "🔄 Reset", PURPLE, (160, 96, 255)
        )
    
    def recalculate_game_layout(self):
        """Recalculate game-specific layout when screen size changes"""
        print("Recalculating Tic Tac Toe layout...")
        self.calculate_grid_layout()
        self.create_game_buttons()
    
    def get_game_info(self):
        return {
            'name': 'Tic Tac Toe',
            'description': 'Classic strategy game with hand tracking',
            'preview_color': CYAN
        }
    
    def reset_game(self):
        """Reset game state"""
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_line = None
        self.cell_animations = [[0 for _ in range(3)] for _ in range(3)]
        
    def get_grid_position(self, x, y):
        """Convert screen coordinates to grid position using dynamic grid"""
        if (x >= self.grid_offset_x and x < self.grid_offset_x + self.grid_size and
            y >= self.grid_offset_y and y < self.grid_offset_y + self.grid_size):
            
            col = (x - self.grid_offset_x) // self.cell_size
            row = (y - self.grid_offset_y) // self.cell_size
            
            if 0 <= row < 3 and 0 <= col < 3:
                return row, col
                
        return None, None
    
    def make_move(self, row, col):
        """Make a move on the board"""
        if (0 <= row < 3 and 0 <= col < 3 and 
            self.board[row][col] == '' and not self.game_over):
            
            self.board[row][col] = self.current_player
            self.cell_animations[row][col] = 1.0  # Start animation
            self.check_winner()
            
            if not self.game_over:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def check_winner(self):
        """Check for winner or draw"""
        # Check rows
        for i, row in enumerate(self.board):
            if row[0] == row[1] == row[2] != '':
                self.winner = row[0]
                self.game_over = True
                self.win_line = ('row', i)
                return
                
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                self.winner = self.board[0][col]
                self.game_over = True
                self.win_line = ('col', col)
                return
                
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            self.winner = self.board[0][0]
            self.game_over = True
            self.win_line = ('diag', 0)
            return
            
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            self.winner = self.board[0][2]
            self.game_over = True
            self.win_line = ('diag', 1)
            return
            
        # Check for draw
        if all(self.board[row][col] != '' for row in range(3) for col in range(3)):
            self.winner = 'Draw'
            self.game_over = True
    
    def handle_game_events(self, event):
        """Handle tic-tac-toe specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check reset button
            if self.reset_button.is_clicked(event.pos, True):
                self.reset_game()
            else:
                # Mouse fallback for game moves
                row, col = self.get_grid_position(event.pos[0], event.pos[1])
                if row is not None and col is not None:
                    self.make_move(row, col)
    
    def update_game(self):
        """Update tic-tac-toe game state"""
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if no hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Handle pinch (rising edge)
        if hand_data.pinching and not self.last_pinch:
            row, col = self.get_grid_position(hand_data.x, hand_data.y)
            if row is not None and col is not None:
                self.make_move(row, col)
                print(f"Pinch detected! Move at ({row}, {col})")
        
        self.last_pinch = hand_data.pinching
        
        # Update reset button
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        self.reset_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Check for hand activation
        if self.reset_button.is_hand_activated():
            self.reset_game()
            print("Game reset by hand gesture!")
        
        # Update cell animations
        for row in range(3):
            for col in range(3):
                if self.cell_animations[row][col] > 0:
                    self.cell_animations[row][col] *= 0.95  # Fade out
    
    def draw_enhanced_grid(self):
        """Draw grid with glowing effects using dynamic positioning"""
        # Draw grid lines with glow
        for i in range(4):
            # Vertical lines
            x = self.grid_offset_x + i * self.cell_size
            pygame.draw.line(self.screen, CYAN, (x, self.grid_offset_y), 
                           (x, self.grid_offset_y + self.grid_size), 4)
            
            # Horizontal lines
            y = self.grid_offset_y + i * self.cell_size
            pygame.draw.line(self.screen, CYAN, (self.grid_offset_x, y), 
                           (self.grid_offset_x + self.grid_size, y), 4)
        
        # Draw cell backgrounds
        for row in range(3):
            for col in range(3):
                x = self.grid_offset_x + col * self.cell_size
                y = self.grid_offset_y + row * self.cell_size
                
                # Animated cell highlight
                if self.cell_animations[row][col] > 0:
                    alpha = int(self.cell_animations[row][col] * 100)
                    highlight_surface = pygame.Surface((self.cell_size - 8, self.cell_size - 8))
                    highlight_surface.set_alpha(alpha)
                    
                    if self.board[row][col] == 'X':
                        highlight_surface.fill(RED)
                    else:
                        highlight_surface.fill(BLUE)
                    
                    self.screen.blit(highlight_surface, (x + 4, y + 4))
    
    def draw_symbols(self):
        """Draw X's and O's with enhanced graphics using dynamic positioning"""
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != '':
                    center_x = self.grid_offset_x + col * self.cell_size + self.cell_size // 2
                    center_y = self.grid_offset_y + row * self.cell_size + self.cell_size // 2
                    
                    if self.board[row][col] == 'X':
                        # Draw enhanced X
                        color = RED
                        size = 60
                        thickness = 8
                        
                        # Draw X with glow effect
                        for offset in range(3):
                            alpha = 255 - offset * 80
                            glow_surface = pygame.Surface((size * 2, size * 2))
                            glow_surface.set_alpha(alpha)
                            
                            pygame.draw.line(glow_surface, color,
                                           (size - size + offset, size - size + offset),
                                           (size + size - offset, size + size - offset), thickness + offset)
                            pygame.draw.line(glow_surface, color,
                                           (size + size - offset, size - size + offset),
                                           (size - size + offset, size + size - offset), thickness + offset)
                            
                            self.screen.blit(glow_surface, (center_x - size, center_y - size))
                    
                    else:  # O
                        # Draw enhanced O
                        color = BLUE
                        radius = 50
                        thickness = 8
                        
                        # Draw O with glow effect
                        for offset in range(3):
                            alpha = 255 - offset * 80
                            glow_surface = pygame.Surface((radius * 2 + 20, radius * 2 + 20))
                            glow_surface.set_alpha(alpha)
                            
                            pygame.draw.circle(glow_surface, color,
                                             (radius + 10, radius + 10), radius + offset, thickness + offset)
                            
                            self.screen.blit(glow_surface, 
                                           (center_x - radius - 10, center_y - radius - 10))
    
    def draw_win_line(self):
        """Draw winning line animation using dynamic positioning"""
        if self.win_line and self.winner != 'Draw':
            line_type, index = self.win_line
            
            # Calculate line positions using dynamic grid
            if line_type == 'row':
                start_x = self.grid_offset_x + 20
                end_x = self.grid_offset_x + self.grid_size - 20
                start_y = end_y = self.grid_offset_y + index * self.cell_size + self.cell_size // 2
            elif line_type == 'col':
                start_x = end_x = self.grid_offset_x + index * self.cell_size + self.cell_size // 2
                start_y = self.grid_offset_y + 20
                end_y = self.grid_offset_y + self.grid_size - 20
            elif line_type == 'diag':
                if index == 0:  # Top-left to bottom-right
                    start_x, start_y = self.grid_offset_x + 20, self.grid_offset_y + 20
                    end_x, end_y = self.grid_offset_x + self.grid_size - 20, self.grid_offset_y + self.grid_size - 20
                else:  # Top-right to bottom-left
                    start_x, start_y = self.grid_offset_x + self.grid_size - 20, self.grid_offset_y + 20
                    end_x, end_y = self.grid_offset_x + 20, self.grid_offset_y + self.grid_size - 20
            
            # Draw glowing win line
            pygame.draw.line(self.screen, YELLOW, (start_x, start_y), (end_x, end_y), 8)
            pygame.draw.line(self.screen, WHITE, (start_x, start_y), (end_x, end_y), 4)
    
    def draw_game(self):
        """Draw tic-tac-toe specific elements"""
        current_width, current_height = self.get_current_screen_size()
        
        # Draw title with logo spacing
        title_text = self.font_title.render("TIC TAC TOE", True, WHITE)
        title_x = 250  # Positioned after logos
        title_y = 40
        self.screen.blit(title_text, (title_x, title_y))
        
        # Draw subtitle
        subtitle_text = self.font_small.render("Hand Tracking Edition", True, CYAN)
        subtitle_x = title_x
        subtitle_y = title_y + 50
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # Draw enhanced grid
        self.draw_enhanced_grid()
        
        # Draw symbols
        self.draw_symbols()
        
        # Highlight current cell
        hand_data = self.hand_tracker.hand_data
        row, col = self.get_grid_position(hand_data.x, hand_data.y)
        if row is not None and col is not None and self.board[row][col] == '' and not self.game_over:
            x = self.grid_offset_x + col * self.cell_size
            y = self.grid_offset_y + row * self.cell_size
            
            highlight_color = YELLOW if hand_data.pinching else GREEN
            alpha = int(150 + math.sin(self.background_manager.time_elapsed * 8) * 50)
            
            highlight_surface = pygame.Surface((self.cell_size - 10, self.cell_size - 10))
            highlight_surface.set_alpha(alpha)
            highlight_surface.fill(highlight_color)
            self.screen.blit(highlight_surface, (x + 5, y + 5))
        
        # Draw win line
        self.draw_win_line()
        
        # Draw hand indicator with pulse
        if hand_data.active and hand_data.hands_count > 0:
            pulse = math.sin(self.background_manager.time_elapsed * 6) * 3 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
        
        # Draw game info panel - Fixed: use dynamic screen size
        panel_y = self.grid_offset_y + self.grid_size + 30
        current_player_text = self.font_medium.render(f"Current Player: {self.current_player}", True, WHITE)
        panel_center_x = current_width // 2  # Fixed: use current screen width
        text_rect = current_player_text.get_rect(center=(panel_center_x, panel_y))
        self.screen.blit(current_player_text, text_rect)
        
        # Status with enhanced styling - Fixed: use dynamic screen size
        if self.game_over:
            if self.winner == 'Draw':
                status = "It's a Draw!"
                status_color = YELLOW
            else:
                status = f"Player {self.winner} Wins!"
                status_color = RED if self.winner == 'X' else BLUE
        else:
            if hand_data.active and hand_data.hands_count > 0:
                status = f"Hand Tracking: {hand_data.hands_count} hands detected"
                status_color = GREEN
            else:
                status = "Using mouse (no hand tracking)"
                status_color = LIGHT_GRAY
                
        status_text = self.font_medium.render(status, True, status_color)
        status_rect = status_text.get_rect(center=(panel_center_x, panel_y + 40))
        self.screen.blit(status_text, status_rect)
        
        # Draw reset button
        self.reset_button.draw(self.screen, self.font_small)
        
        # Instructions - Fixed: use dynamic screen size
        instructions = [
            "Move hand over cell and PINCH to place mark",
            "Hover over buttons for 1 sec or PINCH to activate",
            "Mouse click also works | R: Reset | F11: Fullscreen | ESC: Back to Menu"
        ]
        instruction_y = current_height - 80
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(panel_center_x, instruction_y + i * 25))
            self.screen.blit(text, text_rect)