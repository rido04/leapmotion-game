# games/tic_tac_toe.py
"""
Optimized Tic Tac Toe game - Dark theme with smooth performance
FIXED: Hand indicator now shows on top of win overlay
"""

import pygame
import math
from .base_game import BaseGame
from core import *


class TicTacToeGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Tic Tac Toe - Dark Edition")
        
        # Game state
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_line = None
        
        # Animation states
        self.last_pinch = False
        self.animation_time = 0
        
        # Optimized color scheme for dark background
        self.colors = {
            'bg_overlay': (25, 30, 40, 100),      # Transparent overlay
            'grid_main': (120, 140, 160),         # Steel blue for grid
            'grid_border': (160, 180, 200),       # Border color
            'x_color': (255, 100, 100),           # Bright red for X
            'o_color': (100, 180, 255),           # Bright blue for O
            'win_line': (120, 255, 120),          # Bright green for win line
            'highlight': (255, 255, 120, 80),     # Yellow highlight with alpha
            'text_main': (230, 240, 250),         # Light text
            'text_accent': (160, 200, 255),       # Blue accent
            'button_bg': (70, 80, 100),           # Button background
            'button_hover': (90, 100, 130),       # Button hover
        }
        
        # Layout
        self.calculate_grid_layout()
        self.create_game_buttons()
    
    def calculate_grid_layout(self):
        """Calculate grid layout - larger size"""
        current_width, current_height = self.get_current_screen_size()
        
        # Larger grid size
        self.grid_size = int(min(current_width * 0.45, current_height * 0.55, 450))
        self.cell_size = int(self.grid_size // 3)
        self.grid_offset_x = int((current_width - self.grid_size) // 2)
        self.grid_offset_y = int(max(140, (current_height - self.grid_size) // 2 - 40))
    
    def create_game_buttons(self):
        """Create game buttons"""
        current_width, current_height = self.get_current_screen_size()
        
        # Win overlay button - centered (only one button needed)
        overlay_center_x = current_width // 2
        overlay_center_y = current_height // 2
        
        self.play_again_button = AnimatedButton(
            overlay_center_x - 80, overlay_center_y + 20, 160, 50, "PLAY AGAIN", 
            (60, 100, 60), (80, 120, 80)  # Green button
        )
    
    def recalculate_game_layout(self):
        """Recalculate layout when screen size changes"""
        self.calculate_grid_layout()
        self.create_game_buttons()
    
    def get_game_info(self):
        return {
            'name': 'Tic Tac Toe Dark',
            'description': 'Enhanced strategy game',
            'preview_color': (100, 180, 255)
        }
    
    def reset_game(self):
        """Reset game state"""
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_line = None
        self.animation_time = 0
        
    def get_grid_position(self, x, y):
        """Convert screen coordinates to grid position"""
        try:
            x, y = int(x), int(y)
        except (ValueError, TypeError):
            return None, None
        
        if (x >= self.grid_offset_x and x < self.grid_offset_x + self.grid_size and
            y >= self.grid_offset_y and y < self.grid_offset_y + self.grid_size):
            
            col = int((x - self.grid_offset_x) // self.cell_size)
            row = int((y - self.grid_offset_y) // self.cell_size)
            
            if 0 <= row < 3 and 0 <= col < 3:
                return row, col
                
        return None, None
    
    def make_move(self, row, col):
        """Make a move on the board"""
        if (0 <= row < 3 and 0 <= col < 3 and 
            self.board[row][col] == '' and not self.game_over):
            
            self.board[row][col] = self.current_player
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
        """Handle game events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle win overlay buttons
            if self.game_over:
                if self.play_again_button.is_clicked(event.pos, True):
                    self.reset_game()
            else:
                # Handle game moves during play
                row, col = self.get_grid_position(event.pos[0], event.pos[1])
                if row is not None and col is not None:
                    self.make_move(row, col)
    
    def update_game(self):
        """Update game state"""
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Update animation timer
        self.animation_time += 1
        
        # Safe hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        else:
            try:
                hand_data.x = int(hand_data.x) if hand_data.x is not None else mouse_pos[0]
                hand_data.y = int(hand_data.y) if hand_data.y is not None else mouse_pos[1]
            except:
                hand_data.x, hand_data.y = mouse_pos
        
        # Handle pinch gesture - only during gameplay
        if not self.game_over and hand_data.pinching and not self.last_pinch:
            row, col = self.get_grid_position(hand_data.x, hand_data.y)
            if row is not None and col is not None:
                self.make_move(row, col)
        
        self.last_pinch = hand_data.pinching
        
        # Update win overlay buttons if game is over
        if self.game_over:
            hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
            self.play_again_button.update(mouse_pos, hand_pos, hand_data.pinching)
            
            if self.play_again_button.is_hand_activated():
                self.reset_game()
    
    def draw_grid(self):
        """Draw optimized grid"""
        # Simple background overlay
        overlay_rect = pygame.Rect(self.grid_offset_x - 15, self.grid_offset_y - 15, 
                                 self.grid_size + 30, self.grid_size + 30)
        overlay_surface = pygame.Surface((self.grid_size + 30, self.grid_size + 30))
        overlay_surface.set_alpha(100)
        overlay_surface.fill(self.colors['bg_overlay'][:3])
        self.screen.blit(overlay_surface, (self.grid_offset_x - 15, self.grid_offset_y - 15))
        
        # Draw grid lines - simple and fast
        line_width = 4
        
        for i in range(1, 3):
            # Vertical lines
            x = int(self.grid_offset_x + i * self.cell_size)
            pygame.draw.line(self.screen, self.colors['grid_main'],
                           (x, self.grid_offset_y - 5),
                           (x, self.grid_offset_y + self.grid_size + 5), line_width)
            
            # Horizontal lines
            y = int(self.grid_offset_y + i * self.cell_size)
            pygame.draw.line(self.screen, self.colors['grid_main'],
                           (self.grid_offset_x - 5, y),
                           (self.grid_offset_x + self.grid_size + 5, y), line_width)
        
        # Grid border
        border_rect = pygame.Rect(self.grid_offset_x - 5, self.grid_offset_y - 5, 
                                self.grid_size + 10, self.grid_size + 10)
        pygame.draw.rect(self.screen, self.colors['grid_border'], border_rect, 3)
    
    def draw_symbols(self):
        """Draw X's and O's - optimized"""
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != '':
                    center_x = int(self.grid_offset_x + col * self.cell_size + self.cell_size // 2)
                    center_y = int(self.grid_offset_y + row * self.cell_size + self.cell_size // 2)
                    
                    if self.board[row][col] == 'X':
                        # Draw X - simple and fast
                        size = int(min(self.cell_size // 3, 45))
                        thickness = 6
                        
                        # Shadow effect (simple)
                        shadow_offset = 2
                        shadow_color = (40, 40, 60)
                        pygame.draw.line(self.screen, shadow_color,
                                       (center_x - size + shadow_offset, center_y - size + shadow_offset),
                                       (center_x + size + shadow_offset, center_y + size + shadow_offset), thickness)
                        pygame.draw.line(self.screen, shadow_color,
                                       (center_x + size + shadow_offset, center_y - size + shadow_offset),
                                       (center_x - size + shadow_offset, center_y + size + shadow_offset), thickness)
                        
                        # Main X
                        pygame.draw.line(self.screen, self.colors['x_color'],
                                       (center_x - size, center_y - size),
                                       (center_x + size, center_y + size), thickness)
                        pygame.draw.line(self.screen, self.colors['x_color'],
                                       (center_x + size, center_y - size),
                                       (center_x - size, center_y + size), thickness)
                    
                    else:  # O
                        # Draw O - simple and fast
                        radius = int(min(self.cell_size // 3, 40))
                        thickness = 6
                        
                        # Shadow effect (simple)
                        shadow_offset = 2
                        shadow_color = (40, 40, 60)
                        pygame.draw.circle(self.screen, shadow_color, 
                                         (center_x + shadow_offset, center_y + shadow_offset), 
                                         radius, thickness)
                        
                        # Main O
                        pygame.draw.circle(self.screen, self.colors['o_color'], 
                                         (center_x, center_y), radius, thickness)
    
    def draw_win_line(self):
        """Draw winning line animation"""
        if not self.game_over or not self.win_line:
            return
        
        line_type, index = self.win_line
        line_width = 8
        
        # Pulsing color effect
        pulse = abs(math.sin(self.animation_time * 0.2))
        alpha = int(120 + pulse * 135)
        win_color = (*self.colors['win_line'], alpha)
        
        if line_type == 'row':
            # Horizontal line
            start_x = self.grid_offset_x - 10
            end_x = self.grid_offset_x + self.grid_size + 10
            y = int(self.grid_offset_y + index * self.cell_size + self.cell_size // 2)
            
            # Create surface with alpha
            line_surface = pygame.Surface((end_x - start_x, line_width))
            line_surface.set_alpha(alpha)
            line_surface.fill(self.colors['win_line'])
            self.screen.blit(line_surface, (start_x, y - line_width // 2))
            
        elif line_type == 'col':
            # Vertical line  
            x = int(self.grid_offset_x + index * self.cell_size + self.cell_size // 2)
            start_y = self.grid_offset_y - 10
            end_y = self.grid_offset_y + self.grid_size + 10
            
            # Create surface with alpha
            line_surface = pygame.Surface((line_width, end_y - start_y))
            line_surface.set_alpha(alpha)
            line_surface.fill(self.colors['win_line'])
            self.screen.blit(line_surface, (x - line_width // 2, start_y))
            
        elif line_type == 'diag':
            # Diagonal line
            if index == 0:  # Top-left to bottom-right
                start_x, start_y = self.grid_offset_x - 10, self.grid_offset_y - 10
                end_x, end_y = self.grid_offset_x + self.grid_size + 10, self.grid_offset_y + self.grid_size + 10
            else:  # Top-right to bottom-left
                start_x, start_y = self.grid_offset_x + self.grid_size + 10, self.grid_offset_y - 10
                end_x, end_y = self.grid_offset_x - 10, self.grid_offset_y + self.grid_size + 10
            
            pygame.draw.line(self.screen, self.colors['win_line'],
                           (start_x, start_y), (end_x, end_y), line_width)
    
    def draw_win_overlay(self):
        """Draw win overlay with buttons"""
        if not self.game_over:
            return
            
        current_width, current_height = self.get_current_screen_size()
        
        # Semi-transparent overlay background
        overlay = pygame.Surface((current_width, current_height))
        overlay.set_alpha(180)
        overlay.fill((20, 25, 35))
        self.screen.blit(overlay, (0, 0))
        
        # Win message box
        box_width, box_height = 400, 250
        box_x = (current_width - box_width) // 2
        box_y = (current_height - box_height) // 2
        
        # Box background with border
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.fill((40, 50, 70))
        self.screen.blit(box_surface, (box_x, box_y))
        
        # Box border
        pygame.draw.rect(self.screen, self.colors['grid_border'], 
                        (box_x, box_y, box_width, box_height), 4)
        
        # Win message
        if self.winner == 'Draw':
            main_text = "GAME DRAW!"
            main_color = (255, 200, 100)
            sub_text = "No winner this time"
        else:
            main_text = f"PLAYER {self.winner} WINS!"
            main_color = self.colors['x_color'] if self.winner == 'X' else self.colors['o_color']
            sub_text = "Congratulations!"
        
        # Main win text
        main_font = self.font_title if hasattr(self, 'font_title') else self.font_medium
        win_text = main_font.render(main_text, True, main_color)
        win_rect = win_text.get_rect(center=(current_width // 2, box_y + 60))
        self.screen.blit(win_text, win_rect)
        
        # Sub text
        sub_font = self.font_medium if hasattr(self, 'font_medium') else self.font_small
        sub_rendered = sub_font.render(sub_text, True, self.colors['text_accent'])
        sub_rect = sub_rendered.get_rect(center=(current_width // 2, box_y + 100))
        self.screen.blit(sub_rendered, sub_rect)
        
        # Draw button (single button)
        self.play_again_button.draw(self.screen, self.font_small)

    def draw_hand_indicator(self):
        """Draw hand tracking indicator - separated method for better control"""
        hand_data = self.hand_tracker.hand_data
        try:
            if hand_data.active and hand_data.hands_count > 0:
                hand_x, hand_y = int(hand_data.x), int(hand_data.y)
                
                # Different colors based on state
                if self.game_over:
                    # More visible colors on overlay
                    base_color = (255, 255, 100) if not hand_data.pinching else (100, 255, 100)
                    outer_color = (255, 255, 255)
                else:
                    # Normal game colors
                    base_color = self.colors['o_color'] if not hand_data.pinching else self.colors['x_color']
                    outer_color = (255, 255, 255)
                
                # Draw hand indicator with enhanced visibility
                # Outer ring for better visibility on overlay
                pygame.draw.circle(self.screen, outer_color, (hand_x, hand_y), 15, 2)
                # Inner colored ring
                pygame.draw.circle(self.screen, base_color, (hand_x, hand_y), 12, 3)
                # Center dot
                pygame.draw.circle(self.screen, base_color, (hand_x, hand_y), 4)
                
                # Add small pulsing effect when pinching
                if hand_data.pinching:
                    pulse = int(abs(math.sin(self.animation_time * 0.3)) * 8)
                    pygame.draw.circle(self.screen, base_color, (hand_x, hand_y), 12 + pulse, 1)
                    
        except Exception as e:
            # Fallback to mouse position if hand tracking fails
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (150, 150, 150), mouse_pos, 8, 2)
    
    def draw_game(self):
        """Draw game elements - optimized with proper z-index"""
        current_width, current_height = self.get_current_screen_size()
        
        # Title
        title_text = self.font_title.render("TIC TAC TOE", True, self.colors['text_main'])
        title_rect = title_text.get_rect(center=(current_width // 2, 60))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_small.render("DARK EDITION", True, self.colors['text_accent'])
        subtitle_rect = subtitle_text.get_rect(center=(current_width // 2, 90))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw grid and symbols
        self.draw_grid()
        self.draw_symbols()
        
        # Draw winning line
        self.draw_win_line()
        
        # Simple cell highlight (only if game not over)
        if not self.game_over:
            hand_data = self.hand_tracker.hand_data
            try:
                row, col = self.get_grid_position(hand_data.x, hand_data.y)
                if row is not None and col is not None and self.board[row][col] == '':
                    x = int(self.grid_offset_x + col * self.cell_size)
                    y = int(self.grid_offset_y + row * self.cell_size)
                    
                    # Simple pulsing highlight
                    pulse = int(abs(math.sin(self.animation_time * 0.15)) * 60 + 40)
                    highlight_color = (*self.colors['highlight'][:3], pulse)
                    
                    # Draw highlight
                    highlight_surface = pygame.Surface((self.cell_size, self.cell_size))
                    highlight_surface.set_alpha(pulse)
                    highlight_surface.fill(self.colors['highlight'][:3])
                    self.screen.blit(highlight_surface, (x, y))
                    
                    # Simple border
                    border_color = (255, 255, 150) if not hand_data.pinching else (150, 255, 150)
                    pygame.draw.rect(self.screen, border_color, 
                                   (x, y, self.cell_size, self.cell_size), 3)
            except:
                pass
        
        # Game status (only show if game not over)
        if not self.game_over:
            panel_y = int(self.grid_offset_y + self.grid_size + 40)
            hand_data = self.hand_tracker.hand_data
            
            # Current player
            player_color = self.colors['x_color'] if self.current_player == 'X' else self.colors['o_color']
            current_player_text = self.font_medium.render(f"PLAYER {self.current_player}", True, player_color)
            current_player_rect = current_player_text.get_rect(center=(current_width // 2, panel_y))
            self.screen.blit(current_player_text, current_player_rect)
            
            # Control status
            if hand_data.active and hand_data.hands_count > 0:
                status = "LEAP MOTION READY"
                status_color = self.colors['o_color']
            else:
                status = "MOUSE CONTROL"
                status_color = self.colors['text_accent']
                
            status_text = self.font_medium.render(status, True, status_color)
            status_rect = status_text.get_rect(center=(current_width // 2, panel_y + 35))
            self.screen.blit(status_text, status_rect)
        
        # Instructions (only show if game not over)
        if not self.game_over:
            instructions = [
                "CLICK OR PINCH TO PLAY",
                "R: RESET | F11: FULLSCREEN | ESC: MENU"
            ]
            instruction_y = current_height - 70
            for i, instruction in enumerate(instructions):
                text = self.font_small.render(instruction, True, self.colors['text_accent'])
                text_rect = text.get_rect(center=(current_width // 2, instruction_y + i * 20))
                self.screen.blit(text, text_rect)
        
        # Draw win overlay (this goes BEFORE hand indicator)
        self.draw_win_overlay()
        
        # CRITICAL FIX: Draw hand indicator LAST so it appears on top of everything
        # This ensures the hand tracking pointer is always visible, even over win overlay
        self.draw_hand_indicator()