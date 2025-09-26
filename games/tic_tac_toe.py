# games/competitive_tic_tac_toe.py
"""
Competitive Tic Tac Toe - Enhanced with player names, scores, and virtual keyboard
Features:
- Player name input with virtual keyboard + gesture support
- Daily score tracking
- Enhanced player panels
- Larger grid layout
- Hybrid input (keyboard + gesture)
"""

import pygame
import math
import os
import json
import datetime
from .base_game import BaseGame
from core import *


class VirtualKeyboard:
    """Virtual keyboard with gesture support"""
    def __init__(self, screen_width, screen_height):
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL'],
            ['SPACE']
        ]
        
        self.key_width = 60
        self.key_height = 60
        self.key_margin = 5
        
        # Center the keyboard
        keyboard_width = 10 * (self.key_width + self.key_margin)
        self.start_x = (screen_width - keyboard_width) // 2
        self.start_y = screen_height - 550
        
        self.key_rects = {}
        self.create_key_rects()
        
        self.colors = {
            'key_normal': (60, 70, 90),
            'key_hover': (80, 90, 120),
            'key_pressed': (100, 120, 160),
            'key_text': (220, 230, 250),
            'special_key': (70, 100, 70),  # Green for special keys
            'special_hover': (90, 120, 90)
        }
        
    def create_key_rects(self):
        """Create rectangles for each key"""
        for row_idx, row in enumerate(self.keys):
            # Center each row
            row_width = len(row) * (self.key_width + self.key_margin) - self.key_margin
            if row_idx == 1:  # Second row (ASDF...)
                row_start_x = self.start_x + (self.key_width + self.key_margin) // 2
            elif row_idx == 2:  # Third row (ZXCV...)
                row_start_x = self.start_x + self.key_width + self.key_margin
            elif row_idx == 3:  # Fourth row (SPACE, DONE)
                row_start_x = self.start_x + 2 * (self.key_width + self.key_margin)
            else:  # First row (QWERTY...)
                row_start_x = self.start_x
                
            for col_idx, key in enumerate(row):
                x = row_start_x + col_idx * (self.key_width + self.key_margin)
                y = self.start_y + row_idx * (self.key_height + self.key_margin)
                
                # Special sizing for special keys
                if key == 'SPACE':
                    width = self.key_width * 3
                elif key in ['DEL', 'DONE']:
                    width = int(self.key_width * 1.2)
                else:
                    width = self.key_width
                    
                self.key_rects[key] = pygame.Rect(x, y, width, self.key_height)
    
    def get_key_at_pos(self, pos):
        """Get key at given position"""
        for key, rect in self.key_rects.items():
            if rect.collidepoint(pos):
                return key
        return None
    
    def draw(self, screen, font, hover_pos=None, pressed_key=None):
        """Draw the virtual keyboard"""
        for key, rect in self.key_rects.items():
            # Determine key color
            is_special = key in ['DEL', 'DONE', 'SPACE']
            is_hover = hover_pos and rect.collidepoint(hover_pos)
            is_pressed = key == pressed_key
            
            if is_pressed:
                color = self.colors['key_pressed']
            elif is_hover:
                color = self.colors['special_hover'] if is_special else self.colors['key_hover']
            else:
                color = self.colors['special_key'] if is_special else self.colors['key_normal']
            
            # Draw key background
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (120, 130, 150), rect, 2)
            
            # Draw key text
            display_text = '␣' if key == 'SPACE' else key
            text_surface = font.render(display_text, True, self.colors['key_text'])
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)


class PlayerPanel:
    """Player information panel"""
    def __init__(self, x, y, width, height, player_num):
        self.rect = pygame.Rect(x, y, width, height)
        self.player_num = player_num
        self.name = f"Player {player_num}"
        self.wins_today = 0
        self.is_current = False
        
        # Enhanced color scheme
        if player_num == 1:
        # Player 1 - warna existing (biru)
            self.colors = {
                'panel_bg': (35, 45, 65),
                'panel_active': (50, 70, 100),
                'panel_border': (100, 120, 150),
                'active_border': (80, 200, 80),
                'text_main': (245, 250, 255),
                'text_accent': (255, 255, 255),
                'text_shadow': (15, 20, 30),
                'wins_color': (80, 255, 120),
                'wins_bg': (20, 40, 25),
                'symbol_bg': (45, 55, 75),
                'active_glow': (100, 255, 100, 60)
            }
        else:  # player_num == 2
            # Player 2 - tema hijau gelap
             self.colors = {
                'panel_bg': (20, 35, 20),           # Hijau sangat gelap
                'panel_active': (30, 50, 30),       # Hijau gelap aktif
                'panel_border': (60, 100, 60),      # Hijau redup border
                'active_border': (80, 180, 80),     # Hijau saat aktif
                'text_main': (230, 245, 230),       # Putih kehijauan soft
                'text_accent': (255, 255, 255),     # Hijau muda accent
                'text_shadow': (8, 20, 8),          # Shadow hijau sangat gelap
                'wins_color': (100, 220, 100),      # Hijau medium score
                'wins_bg': (12, 25, 12),            # Background score hijau gelap
                'symbol_bg': (25, 40, 25),          # Background symbol
                'active_glow': (80, 200, 80, 60)    # Glow hijau
            }
    
    def draw(self, screen, font_medium, font_small, font_digital, symbol_image=None):
        """Draw the player panel"""
        # Background color based on active state
        bg_color = self.colors['panel_active'] if self.is_current else self.colors['panel_bg']
        border_color = self.colors['active_border'] if self.is_current else self.colors['panel_border']
        
        # Draw panel background
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 3 if self.is_current else 2)
        
        # Player symbol at top (made bigger)
        symbol_y = self.rect.y + 20
        if symbol_image:
            # Use provided symbol image - scale it up to make it bigger
            original_size = symbol_image.get_size()
            scale_factor = 1.5  # Make it 50% bigger, adjust this value as needed
            new_width = int(original_size[0] * scale_factor)
            new_height = int(original_size[1] * scale_factor)
            
            scaled_symbol = pygame.transform.scale(symbol_image, (new_width, new_height))
            symbol_rect = scaled_symbol.get_rect()
            symbol_rect.center = (self.rect.centerx, symbol_y + 40)  # Adjusted position
            screen.blit(scaled_symbol, symbol_rect)
            name_y = symbol_y + 100  # Adjusted spacing
        else:
            # Fallback text symbol - made bigger
            symbol_text = "X" if self.player_num == 1 else "O"
            symbol_color = (255, 100, 100) if self.player_num == 1 else (100, 180, 255)
            # Use a larger font or scale up the text
            symbol_surface = font_medium.render(symbol_text, True, symbol_color)
            # Scale up the text symbol
            scaled_symbol = pygame.transform.scale(symbol_surface, 
                                                (int(symbol_surface.get_width() * 1.5), 
                                                int(symbol_surface.get_height() * 1.5)))
            symbol_rect = scaled_symbol.get_rect(center=(self.rect.centerx, symbol_y + 20))
            screen.blit(scaled_symbol, symbol_rect)
            name_y = symbol_y + 60
        
        # Player name
        name_surface = font_medium.render(self.name[:12], True, self.colors['text_main'])  # Limit name length
        name_rect = name_surface.get_rect(center=(self.rect.centerx, name_y))
        screen.blit(name_surface, name_rect)
        
        # Wins today label
        wins_label = "Wins Today:"
        wins_label_surface = font_small.render(wins_label, True, self.colors['wins_color'])
        wins_label_rect = wins_label_surface.get_rect(center=(self.rect.centerx, name_y + 40))
        screen.blit(wins_label_surface, wins_label_rect)

        # Score number dengan margin lebih besar dari label
        score_text = str(self.wins_today)
        original_surface = font_digital.render(score_text, True, self.colors['wins_color'])

        # Scale up score
        scale_factor = 3
        new_width = int(original_surface.get_width() * scale_factor)
        new_height = int(original_surface.get_height() * scale_factor)
        score_surface = pygame.transform.scale(original_surface, (new_width, new_height))

        # Positioning dengan margin lebih besar (ubah +65 jadi +80 atau lebih)
        margin_from_label = 55  # Margin dari "Wins Today"
        score_rect = score_surface.get_rect(center=(self.rect.centerx, name_y + 40 + margin_from_label))
        screen.blit(score_surface, score_rect)
        
        # Current player indicator
        if self.is_current:
            indicator_text = "YOUR TURN"
            indicator_surface = font_small.render(indicator_text, True, self.colors['active_border'])
            indicator_rect = indicator_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 30))
            screen.blit(indicator_surface, indicator_rect)


class TicTacToeGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Competitive Tic Tac Toe")
        
        # Game states
        self.game_state = 'name_input'  # 'name_input', 'playing', 'game_over'
        self.current_name_player = 1
        self.input_text = ""
        self.cursor_blink = 0
        
        # Game state
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 1  # 1 or 2
        self.winner = None
        self.game_over = False
        self.win_line = None
        
        # Animation and interaction
        self.last_pinch = False
        self.animation_time = 0
        self.last_key_press = None
        self.key_press_time = 0
        
        # fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        
        # Font "digital" menggunakan monospace dengan ukuran lebih besar
        try:
        # Coba load font digital
            self.font_digital = pygame.font.Font("assets/fonts/digital/DS-DIGI.TTF", 32)
        except:
            # Fallback jika font tidak ada
            self.font_digital = pygame.font.Font(None, 32)
        # Load and scale images
        self.load_symbol_images()
        
        # Enhanced color scheme
        self.colors = {
            'bg_main': (25, 30, 40),
            'bg_overlay': (25, 30, 40, 150),
            'grid_main': (120, 140, 160),
            'grid_border': (160, 180, 200),
            'player1_color': (255, 100, 100),  # Red for Player 1
            'player2_color': (100, 180, 255),  # Blue for Player 2
            'win_line': (120, 255, 120),
            'highlight': (255, 255, 120, 80),
            'text_main': (230, 240, 250),
            'text_accent': (160, 200, 255),
            'input_bg': (50, 60, 80),
            'input_active': (70, 80, 110),
            'cursor_color': (255, 255, 255)
        }
        
        # Create virtual keyboard
        current_width, current_height = self.get_current_screen_size()
        self.virtual_keyboard = VirtualKeyboard(current_width, current_height)
        
        # Player data
        self.players = {
            1: PlayerPanel(50, 100, 200, 300, 1),
            2: PlayerPanel(current_width - 250, 100, 200, 300, 2)
        }
        self.players[1].is_current = True
        
        # Load daily scores
        self.load_daily_scores()
        
        # Layout calculation
        self.calculate_enhanced_layout()
        self.create_game_buttons()
    
    def load_symbol_images(self):
        """Load and scale PNG images for symbols"""
        try:
            assets_path = os.path.join("assets", "tic-tac-toe")
            
            # Load images
            x_image_path = os.path.join(assets_path, "3-stripes-w.png")
            o_image_path = os.path.join(assets_path, "3-foil-w2.png")
            
            self.x_image_original = pygame.image.load(x_image_path)
            self.o_image_original = pygame.image.load(o_image_path)
            
            self.x_image_scaled = None
            self.o_image_scaled = None
            self.x_image_panel = None  # For player panels
            self.o_image_panel = None
            
        except pygame.error as e:
            print(f"Error loading symbol images: {e}")
            self.x_image_original = None
            self.o_image_original = None
            self.x_image_scaled = None
            self.o_image_scaled = None
            self.x_image_panel = None
            self.o_image_panel = None
    
    def scale_symbol_images(self):
        """Scale images for both game grid and player panels"""
        if self.x_image_original is None or self.o_image_original is None:
            return
            
        try:
            # For game grid (80% of cell size)
            grid_target_size = int(self.cell_size * 0.8)
            
            # Scale X for grid
            x_width = grid_target_size
            x_height = int(grid_target_size * 283 / 405)
            self.x_image_scaled = pygame.transform.smoothscale(
                self.x_image_original, (x_width, x_height)
            )
            
            # Scale O for grid
            self.o_image_scaled = pygame.transform.smoothscale(
                self.o_image_original, (grid_target_size, grid_target_size)
            )
            
            # For player panels (smaller size)
            panel_size = 50
            
            # Scale X for panel
            panel_x_width = panel_size
            panel_x_height = int(panel_size * 283 / 405)
            self.x_image_panel = pygame.transform.smoothscale(
                self.x_image_original, (panel_x_width, panel_x_height)
            )
            
            # Scale O for panel
            self.o_image_panel = pygame.transform.smoothscale(
                self.o_image_original, (panel_size, panel_size)
            )
            
        except Exception as e:
            print(f"Error scaling images: {e}")
            self.x_image_scaled = None
            self.o_image_scaled = None
            self.x_image_panel = None
            self.o_image_panel = None
    
    def calculate_enhanced_layout(self):
        """Calculate enhanced layout with larger grid and player panels"""
        current_width, current_height = self.get_current_screen_size()
        
        # Grid yang lebih besar untuk display besar
        available_width = current_width - 600  # Lebih banyak space untuk player panels
        # Perbesar grid size minimum dan maximum
        min_grid_size = 600  # Minimum grid size untuk display besar
        max_grid_size = 800  # Maximum grid size
        
        self.grid_size = int(max(min_grid_size, min(available_width * 0.9, current_height * 0.7, max_grid_size)))
        self.cell_size = int(self.grid_size // 3)
        self.grid_offset_x = int((current_width - self.grid_size) // 2)
        self.grid_offset_y = int(max(140, (current_height - self.grid_size) // 2 - 30))
        
        # Player panels yang lebih besar dan lebih cantik
        panel_width = 280  # Lebih lebar
        panel_height = 400  # Lebih tinggi
        panel_margin = 60   # Margin dari tepi
        
        self.players[1].rect = pygame.Rect(panel_margin, 120, panel_width, panel_height)
        self.players[2].rect = pygame.Rect(current_width - panel_margin - panel_width, 120, panel_width, panel_height)
        
        # Scale images
        self.scale_symbol_images()
        
        # Recreate virtual keyboard for new screen size
        self.virtual_keyboard = VirtualKeyboard(current_width, current_height)
    
    def create_game_buttons(self):
        """Create game buttons"""
        current_width, current_height = self.get_current_screen_size()
        
        # Buttons for different states
        center_x = current_width // 2
        
        # Name input buttons
        self.next_button = AnimatedButton(
            center_x - 50, current_height - 600, 100, 40, "NEXT", 
            (60, 100, 60), (80, 120, 80)
        )
        
        self.start_game_button = AnimatedButton(
            center_x - 60, current_height - 600, 120, 40, "START GAME", 
            (60, 100, 60), (80, 120, 80)
        )
        
        # Game over buttons - BERDAMPINGAN
        button_width = 140
        button_height = 50
        button_spacing = 20  # Jarak antara button
        
        # Hitung posisi agar kedua button centered
        total_width = (button_width * 2) + button_spacing
        start_x = center_x - (total_width // 2)
        
        self.play_again_button = AnimatedButton(
            start_x, current_height // 2 + 50, button_width, button_height, "PLAY AGAIN", 
            (60, 100, 60), (0, 0, 0)
        )

        self.new_players_button = AnimatedButton(
            start_x + button_width + button_spacing, current_height // 2 + 50, button_width, button_height, "NEW PLAYERS", 
            (100, 60, 60), (0, 0, 0)
        )
    
    def load_daily_scores(self):
        """Load daily scores from file"""
        today = datetime.date.today().isoformat()
        try:
            with open('daily_scores.json', 'r') as f:
                data = json.load(f)
                if data.get('date') == today:
                    # Load today's scores
                    scores = data.get('scores', {})
                    self.players[1].wins_today = scores.get('player1', 0)
                    self.players[2].wins_today = scores.get('player2', 0)
                    # Load names if available
                    names = data.get('names', {})
                    if 'player1' in names:
                        self.players[1].name = names['player1']
                    if 'player2' in names:
                        self.players[2].name = names['player2']
                else:
                    # New day, reset scores
                    self.save_daily_scores()
        except FileNotFoundError:
            self.save_daily_scores()
    
    def save_daily_scores(self):
        """Save daily scores to file"""
        today = datetime.date.today().isoformat()
        data = {
            'date': today,
            'scores': {
                'player1': self.players[1].wins_today,
                'player2': self.players[2].wins_today
            },
            'names': {
                'player1': self.players[1].name,
                'player2': self.players[2].name
            }
        }
        try:
            with open('daily_scores.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def get_game_info(self):
        return {
            'name': 'Competitive Tic Tac Toe',
            'description': 'Enhanced multiplayer with scoring',
            'preview_color': (100, 180, 255)
        }
    
    def reset_game_only(self):
        """Reset only the game board, keep players and scores"""
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 1
        self.winner = None
        self.game_over = False
        self.win_line = None
        self.animation_time = 0
        # Jangan ubah game_state di sini, biarkan method pemanggil yang menentukan
        
        # Update current player indicator
        self.players[1].is_current = True
        self.players[2].is_current = False

    def reset_all(self):
        """Reset everything including players"""
        # Reset ke input nama
        self.game_state = 'name_input'
        self.current_name_player = 1
        self.input_text = ""
        
        # Reset player data
        self.players[1].name = "Player 1"
        self.players[2].name = "Player 2" 
        self.players[1].wins_today = 0
        self.players[2].wins_today = 0
        
        # Reset game board tanpa mengubah game_state
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 1
        self.winner = None
        self.game_over = False
        self.win_line = None
        self.animation_time = 0
        self.players[1].is_current = True
        self.players[2].is_current = False
        
        # Hapus file daily scores agar tidak di-load ulang
        try:
            if os.path.exists('daily_scores.json'):
                os.remove('daily_scores.json')
        except Exception:
            pass
    
    def handle_text_input(self, text):
        """Handle text input for names"""
        if self.game_state != 'name_input':
            return
            
        if text == 'DEL':
            if self.input_text:
                self.input_text = self.input_text[:-1]
        elif text == 'SPACE':
            if len(self.input_text) < 15:
                self.input_text += ' '
        elif text == 'DONE':
            if self.input_text.strip():
                self.players[self.current_name_player].name = self.input_text.strip()
                if self.current_name_player == 1:
                    self.current_name_player = 2
                    self.input_text = ""
                else:
                    self.game_state = 'playing'
                    self.save_daily_scores()
        elif len(text) == 1 and text.isalpha() and len(self.input_text) < 15:
            self.input_text += text
    
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
            self.board[row][col] == '' and not self.game_over and 
            self.game_state == 'playing'):
            
            self.board[row][col] = str(self.current_player)
            self.check_winner()
            
            if not self.game_over:
                # Switch players
                self.current_player = 2 if self.current_player == 1 else 1
                self.players[1].is_current = (self.current_player == 1)
                self.players[2].is_current = (self.current_player == 2)
    
    def check_winner(self):
        """Check for winner or draw"""
        player_symbol = str(self.current_player)
        
        # Check rows
        for i, row in enumerate(self.board):
            if row[0] == row[1] == row[2] == player_symbol:
                self.winner = self.current_player
                self.game_over = True
                self.win_line = ('row', i)
                self.game_state = 'game_over'
                self.players[self.current_player].wins_today += 1
                self.save_daily_scores()
                return
                
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] == player_symbol:
                self.winner = self.current_player
                self.game_over = True
                self.win_line = ('col', col)
                self.game_state = 'game_over'
                self.players[self.current_player].wins_today += 1
                self.save_daily_scores()
                return
                
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player_symbol:
            self.winner = self.current_player
            self.game_over = True
            self.win_line = ('diag', 0)
            self.game_state = 'game_over'
            self.players[self.current_player].wins_today += 1
            self.save_daily_scores()
            return
            
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == player_symbol:
            self.winner = self.current_player
            self.game_over = True
            self.win_line = ('diag', 1)
            self.game_state = 'game_over'
            self.players[self.current_player].wins_today += 1
            self.save_daily_scores()
            return
            
        # Check for draw
        if all(self.board[row][col] != '' for row in range(3) for col in range(3)):
            self.winner = 'Draw'
            self.game_over = True
            self.game_state = 'game_over'
    
    def handle_game_events(self, event):
        """Handle game events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game_state == 'playing':
                self.reset_game_only()
            elif self.game_state == 'name_input':
                # Handle keyboard input for names
                if event.key == pygame.K_BACKSPACE:
                    self.handle_text_input('DEL')
                elif event.key == pygame.K_SPACE:
                    self.handle_text_input('SPACE')
                elif event.key == pygame.K_RETURN:
                    self.handle_text_input('DONE')
                elif event.unicode and event.unicode.isalpha():
                    self.handle_text_input(event.unicode.upper())
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if self.game_state == 'name_input':
                # Check virtual keyboard
                key = self.virtual_keyboard.get_key_at_pos(mouse_pos)
                if key:
                    self.handle_text_input(key)
                    self.last_key_press = key
                    self.key_press_time = self.animation_time
                
                # Check buttons
                if self.current_name_player == 1 and self.input_text.strip():
                    if self.next_button.is_clicked(mouse_pos, True):
                        self.handle_text_input('DONE')
                elif self.current_name_player == 2 and self.input_text.strip():
                    if self.start_game_button.is_clicked(mouse_pos, True):
                        self.handle_text_input('DONE')
                        
            elif self.game_state == 'playing':
                # Handle game moves
                row, col = self.get_grid_position(mouse_pos[0], mouse_pos[1])
                if row is not None and col is not None:
                    self.make_move(row, col)
                    
            elif self.game_state == 'game_over':
                # Handle game over buttons
                if self.play_again_button.is_clicked(mouse_pos, True):
                    self.reset_game_only()
                    self.game_state = 'playing'
                elif self.new_players_button.is_clicked(mouse_pos, True):
                    self.reset_all()
    
    def update_game(self):
        """Update game state"""
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        self.animation_time += 1
        self.cursor_blink += 1
        
        # Safe hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        else:
            try:
                hand_data.x = int(hand_data.x) if hand_data.x is not None else mouse_pos[0]
                hand_data.y = int(hand_data.y) if hand_data.y is not None else mouse_pos[1]
            except:
                hand_data.x, hand_data.y = mouse_pos
        
        # Handle pinch gestures
        if hand_data.pinching and not self.last_pinch:
            if self.game_state == 'name_input':
                # Virtual keyboard interaction
                key = self.virtual_keyboard.get_key_at_pos((hand_data.x, hand_data.y))
                if key:
                    self.handle_text_input(key)
                    self.last_key_press = key
                    self.key_press_time = self.animation_time
                    
            elif self.game_state == 'playing':
                # Game move
                row, col = self.get_grid_position(hand_data.x, hand_data.y)
                if row is not None and col is not None:
                    self.make_move(row, col)
                    
            elif self.game_state == 'game_over':
                # Game over buttons
                hand_pos = (hand_data.x, hand_data.y)
                if self.play_again_button.rect.collidepoint(hand_pos):
                    self.reset_game_only()
                elif self.new_players_button.rect.collidepoint(hand_pos):
                    self.reset_all()
        
        self.last_pinch = hand_data.pinching
        
        # Update buttons based on game state
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        
        if self.game_state == 'name_input':
            if self.current_name_player == 1 and self.input_text.strip():
                self.next_button.update(mouse_pos, hand_pos, hand_data.pinching)
                if self.next_button.is_hand_activated():
                    self.handle_text_input('DONE')
            elif self.current_name_player == 2 and self.input_text.strip():
                self.start_game_button.update(mouse_pos, hand_pos, hand_data.pinching)
                if self.start_game_button.is_hand_activated():
                    self.handle_text_input('DONE')
                    
        elif self.game_state == 'game_over':
            self.play_again_button.update(mouse_pos, hand_pos, hand_data.pinching)
            self.new_players_button.update(mouse_pos, hand_pos, hand_data.pinching)
            
            if self.play_again_button.is_hand_activated():
                self.reset_game_only()
                self.game_state = 'playing'
            elif self.new_players_button.is_hand_activated():
                self.reset_all()
    
    def recalculate_game_layout(self):
        """Recalculate layout when screen size changes"""
        self.calculate_enhanced_layout()
        self.create_game_buttons()
    
    def draw_name_input_screen(self):
        """Draw name input screen"""
        current_width, current_height = self.get_current_screen_size()
        
        # Title
        # title_text = "COMPETITIVE TIC TAC TOE"
        # title_surface = self.font_medium.render(title_text, True, self.colors['text_main'])
        # title_rect = title_surface.get_rect(center=(current_width // 2, 80))
        # self.screen.blit(title_surface, title_rect)
        
        # Player input prompt
        prompt_text = f"Enter name for Player {self.current_name_player}:"
        prompt_surface = self.font_medium.render(prompt_text, True, self.colors['text_accent'])
        prompt_rect = prompt_surface.get_rect(center=(current_width // 2, 140))
        self.screen.blit(prompt_surface, prompt_rect)
        
        # Input box
        input_box_width = 300
        input_box_height = 50
        input_box_x = (current_width - input_box_width) // 2
        input_box_y = 180
        
        input_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
        input_bg_color = self.colors['input_active'] if self.input_text else self.colors['input_bg']
        
        pygame.draw.rect(self.screen, input_bg_color, input_rect)
        pygame.draw.rect(self.screen, self.colors['text_accent'], input_rect, 2)
        
        # Input text
        if self.input_text:
            text_surface = self.font_medium.render(self.input_text, True, self.colors['text_main'])
            text_rect = text_surface.get_rect(center=input_rect.center)
            self.screen.blit(text_surface, text_rect)
        else:
            placeholder = f"Player {self.current_name_player}"
            placeholder_surface = self.font_medium.render(placeholder, True, (120, 130, 140))
            placeholder_rect = placeholder_surface.get_rect(center=input_rect.center)
            self.screen.blit(placeholder_surface, placeholder_rect)
        
        # Blinking cursor
        if self.cursor_blink % 60 < 30 and self.input_text:
            cursor_x = text_rect.right + 5
            cursor_y1 = input_rect.centery - 15
            cursor_y2 = input_rect.centery + 15
            pygame.draw.line(self.screen, self.colors['cursor_color'], 
                           (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
        
        # Virtual keyboard
        hand_data = self.hand_tracker.hand_data
        hover_pos = (hand_data.x, hand_data.y) if hand_data.active and hand_data.hands_count > 0 else pygame.mouse.get_pos()
        pressed_key = self.last_key_press if (self.animation_time - self.key_press_time) < 10 else None
        
        self.virtual_keyboard.draw(self.screen, self.font_small, hover_pos, pressed_key)
        
        # Navigation buttons
        if self.current_name_player == 1 and self.input_text.strip():
            self.next_button.draw(self.screen, self.font_small)
        elif self.current_name_player == 2 and self.input_text.strip():
            self.start_game_button.draw(self.screen, self.font_small)
        
        # Instructions
        instructions = [
            "Use keyboard or click/pinch virtual keys"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, self.colors['text_accent'])
            text_rect = text.get_rect(center=(current_width // 2, 50 + i * 20))
            self.screen.blit(text, text_rect)
    
    def draw_grid(self):
        """Draw enhanced game grid"""
        # Background overlay
        overlay_rect = pygame.Rect(self.grid_offset_x - 20, self.grid_offset_y - 20, 
                                 self.grid_size + 40, self.grid_size + 40)
        overlay_surface = pygame.Surface((self.grid_size + 40, self.grid_size + 40))
        overlay_surface.set_alpha(120)
        overlay_surface.fill(self.colors['bg_overlay'][:3])
        self.screen.blit(overlay_surface, (self.grid_offset_x - 20, self.grid_offset_y - 20))
        
        # Draw grid lines
        line_width = 5
        
        for i in range(1, 3):
            # Vertical lines
            x = int(self.grid_offset_x + i * self.cell_size)
            pygame.draw.line(self.screen, self.colors['grid_main'],
                           (x, self.grid_offset_y - 10),
                           (x, self.grid_offset_y + self.grid_size + 10), line_width)
            
            # Horizontal lines
            y = int(self.grid_offset_y + i * self.cell_size)
            pygame.draw.line(self.screen, self.colors['grid_main'],
                           (self.grid_offset_x - 10, y),
                           (self.grid_offset_x + self.grid_size + 10, y), line_width)
        
        # Grid border
        border_rect = pygame.Rect(self.grid_offset_x - 10, self.grid_offset_y - 10, 
                                self.grid_size + 20, self.grid_size + 20)
        pygame.draw.rect(self.screen, self.colors['grid_border'], border_rect, 4)
    
    def draw_symbols(self):
        """Draw game symbols using images or fallback"""
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != '':
                    center_x = int(self.grid_offset_x + col * self.cell_size + self.cell_size // 2)
                    center_y = int(self.grid_offset_y + row * self.cell_size + self.cell_size // 2)
                    
                    player = int(self.board[row][col])
                    
                    if player == 1:  # Player 1 - X
                        if self.x_image_scaled is not None:
                            image_rect = self.x_image_scaled.get_rect()
                            image_rect.center = (center_x, center_y)
                            
                            # Shadow
                            shadow_offset = 4
                            shadow_surface = pygame.Surface(self.x_image_scaled.get_size())
                            shadow_surface.fill((40, 40, 60))
                            shadow_surface.set_alpha(120)
                            shadow_rect = shadow_surface.get_rect()
                            shadow_rect.center = (center_x + shadow_offset, center_y + shadow_offset)
                            self.screen.blit(shadow_surface, shadow_rect)
                            
                            self.screen.blit(self.x_image_scaled, image_rect)
                        else:
                            # Fallback drawn X
                            size = int(min(self.cell_size // 3, 60))
                            thickness = 8
                            pygame.draw.line(self.screen, self.colors['player1_color'],
                                           (center_x - size, center_y - size),
                                           (center_x + size, center_y + size), thickness)
                            pygame.draw.line(self.screen, self.colors['player1_color'],
                                           (center_x + size, center_y - size),
                                           (center_x - size, center_y + size), thickness)
                    
                    else:  # Player 2 - O
                        if self.o_image_scaled is not None:
                            image_rect = self.o_image_scaled.get_rect()
                            image_rect.center = (center_x, center_y)
                            
                            # Shadow
                            shadow_offset = 4
                            shadow_surface = pygame.Surface(self.o_image_scaled.get_size())
                            shadow_surface.fill((40, 40, 60))
                            shadow_surface.set_alpha(120)
                            shadow_rect = shadow_surface.get_rect()
                            shadow_rect.center = (center_x + shadow_offset, center_y + shadow_offset)
                            self.screen.blit(shadow_surface, shadow_rect)
                            
                            self.screen.blit(self.o_image_scaled, image_rect)
                        else:
                            # Fallback drawn O
                            radius = int(min(self.cell_size // 3, 50))
                            thickness = 8
                            pygame.draw.circle(self.screen, self.colors['player2_color'], 
                                             (center_x, center_y), radius, thickness)
    
    def draw_win_line(self):
        """Draw winning line with animation"""
        if not self.game_over or not self.win_line:
            return
        
        line_type, index = self.win_line
        line_width = 10
        
        # Pulsing effect
        pulse = abs(math.sin(self.animation_time * 0.2))
        alpha = int(150 + pulse * 105)
        
        if line_type == 'row':
            start_x = self.grid_offset_x - 15
            end_x = self.grid_offset_x + self.grid_size + 15
            y = int(self.grid_offset_y + index * self.cell_size + self.cell_size // 2)
            
            line_surface = pygame.Surface((end_x - start_x, line_width))
            line_surface.set_alpha(alpha)
            line_surface.fill(self.colors['win_line'])
            self.screen.blit(line_surface, (start_x, y - line_width // 2))
            
        elif line_type == 'col':
            x = int(self.grid_offset_x + index * self.cell_size + self.cell_size // 2)
            start_y = self.grid_offset_y - 15
            end_y = self.grid_offset_y + self.grid_size + 15
            
            line_surface = pygame.Surface((line_width, end_y - start_y))
            line_surface.set_alpha(alpha)
            line_surface.fill(self.colors['win_line'])
            self.screen.blit(line_surface, (x - line_width // 2, start_y))
            
        elif line_type == 'diag':
            if index == 0:
                start_x, start_y = self.grid_offset_x - 15, self.grid_offset_y - 15
                end_x, end_y = self.grid_offset_x + self.grid_size + 15, self.grid_offset_y + self.grid_size + 15
            else:
                start_x, start_y = self.grid_offset_x + self.grid_size + 15, self.grid_offset_y - 15
                end_x, end_y = self.grid_offset_x - 15, self.grid_offset_y + self.grid_size + 15
            
            pygame.draw.line(self.screen, self.colors['win_line'],
                           (start_x, start_y), (end_x, end_y), line_width)
    
    def draw_game_over_overlay(self):
        """Draw game over overlay"""
        if self.game_state != 'game_over':
            return
            
        current_width, current_height = self.get_current_screen_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((current_width, current_height))
        overlay.set_alpha(200)
        overlay.fill((20, 25, 35))
        self.screen.blit(overlay, (0, 0))
        
        # Win message box
        box_width, box_height = 450, 300
        box_x = (current_width - box_width) // 2
        box_y = (current_height - box_height) // 2
        
        # Box background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.fill((40, 50, 70))
        self.screen.blit(box_surface, (box_x, box_y))
        
        # Box border
        pygame.draw.rect(self.screen, self.colors['grid_border'], 
                        (box_x, box_y, box_width, box_height), 5)
        
        # Win message
        if self.winner == 'Draw':
            main_text = "GAME DRAW!"
            main_color = (255, 200, 100)
            sub_text = "No winner this time"
        else:
            winner_name = self.players[self.winner].name
            main_text = f"{winner_name.upper()} WINS!"
            main_color = self.colors['player1_color'] if self.winner == 1 else self.colors['player2_color']
            sub_text = "Congratulations!"
        
        # Main text
        main_font = self.font_medium
        win_text = main_font.render(main_text, True, main_color)
        win_rect = win_text.get_rect(center=(current_width // 2, box_y + 70))
        self.screen.blit(win_text, win_rect)
        
        # Sub text
        sub_rendered = self.font_small.render(sub_text, True, self.colors['text_accent'])
        sub_rect = sub_rendered.get_rect(center=(current_width // 2, box_y + 110))
        self.screen.blit(sub_rendered, sub_rect)
        
        # Current scores
        score_text = f"{self.players[1].name}: {self.players[1].wins_today} wins today"
        score1 = self.font_small.render(score_text, True, self.colors['player1_color'])
        score1_rect = score1.get_rect(center=(current_width // 2, box_y + 150))
        self.screen.blit(score1, score1_rect)
        
        score_text = f"{self.players[2].name}: {self.players[2].wins_today} wins today"
        score2 = self.font_small.render(score_text, True, self.colors['player2_color'])
        score2_rect = score2.get_rect(center=(current_width // 2, box_y + 175))
        self.screen.blit(score2, score2_rect)
        
        # Buttons
        self.play_again_button.draw(self.screen, self.font_small)
        self.new_players_button.draw(self.screen, self.font_small)
    
    def draw_hand_indicator(self):
        """Draw hand tracking indicator"""
        hand_data = self.hand_tracker.hand_data
        try:
            if hand_data.active and hand_data.hands_count > 0:
                hand_x, hand_y = int(hand_data.x), int(hand_data.y)
                
                # Color based on game state and player
                if self.game_state == 'playing':
                    base_color = self.colors['player1_color'] if self.current_player == 1 else self.colors['player2_color']
                    if hand_data.pinching:
                        base_color = self.colors['win_line']
                else:
                    base_color = (255, 255, 100) if not hand_data.pinching else (100, 255, 100)
                
                outer_color = (255, 255, 255)
                
                # Draw indicator
                pygame.draw.circle(self.screen, outer_color, (hand_x, hand_y), 18, 2)
                pygame.draw.circle(self.screen, base_color, (hand_x, hand_y), 15, 3)
                pygame.draw.circle(self.screen, base_color, (hand_x, hand_y), 6)
                
                # Pulsing when pinching
                if hand_data.pinching:
                    pulse = int(abs(math.sin(self.animation_time * 0.4)) * 10)
                    pygame.draw.circle(self.screen, base_color, (hand_x, hand_y), 15 + pulse, 1)
                    
        except Exception:
            # Fallback to mouse
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, (150, 150, 150), mouse_pos, 10, 2)
    
    def draw_game(self):
        """Main draw method"""
        current_width, current_height = self.get_current_screen_size()
        
        if self.game_state == 'name_input':
            self.draw_name_input_screen()
            
        else:  # playing or game_over
            # Draw player panels
            player1_symbol = self.x_image_panel if self.x_image_panel else None
            player2_symbol = self.o_image_panel if self.o_image_panel else None
            
            self.players[1].draw(self.screen, self.font_medium, self.font_small, self.font_digital, player1_symbol)
            self.players[2].draw(self.screen, self.font_medium, self.font_small, self.font_digital, player2_symbol)
            
            # Draw game grid and symbols
            self.draw_grid()
            self.draw_symbols()
            self.draw_win_line()
            
            # Cell highlight (only during gameplay)
            if self.game_state == 'playing':
                hand_data = self.hand_tracker.hand_data
                try:
                    row, col = self.get_grid_position(hand_data.x, hand_data.y)
                    if row is not None and col is not None and self.board[row][col] == '':
                        x = int(self.grid_offset_x + col * self.cell_size)
                        y = int(self.grid_offset_y + row * self.cell_size)
                        
                        # Pulsing highlight
                        pulse = int(abs(math.sin(self.animation_time * 0.2)) * 80 + 60)
                        highlight_color = (*self.colors['highlight'][:3], pulse)
                        
                        highlight_surface = pygame.Surface((self.cell_size, self.cell_size))
                        highlight_surface.set_alpha(pulse)
                        highlight_surface.fill(self.colors['highlight'][:3])
                        self.screen.blit(highlight_surface, (x, y))
                        
                        # Border
                        current_player_color = self.colors['player1_color'] if self.current_player == 1 else self.colors['player2_color']
                        if hand_data.pinching:
                            current_player_color = self.colors['win_line']
                            
                        pygame.draw.rect(self.screen, current_player_color, 
                                       (x, y, self.cell_size, self.cell_size), 4)
                except:
                    pass
            
            # Game info (only during gameplay)
            if self.game_state == 'playing':
                # Control instructions
                instructions = [
                    "Click or Pinch to play • R: Reset • F11: Fullscreen • ESC: Menu",
                    "Developed and Maintained by GVI PT. Maxima Cipta Miliardatha development team"
                ]
                
                for i, instruction in enumerate(instructions):
                    text = self.font_small.render(instruction, True, self.colors['text_accent'])
                    text_rect = text.get_rect(center=(current_width // 2, current_height - 40 + i * 20))
                    self.screen.blit(text, text_rect)
            
            # Draw game over overlay
            self.draw_game_over_overlay()
        
        # Always draw hand indicator last
        self.draw_hand_indicator()