import pygame
import sys
import leap
import time
import threading
import math
import random
import os
from dataclasses import dataclass

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
GRID_SIZE = 450
CELL_SIZE = GRID_SIZE // 3
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_SIZE) // 2
GRID_OFFSET_Y = 180

# Enhanced Colors with gradients
WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
DARK_GRAY = (40, 40, 50)
LIGHT_GRAY = (100, 100, 120)
BLUE = (64, 128, 255)
BLUE_DARK = (32, 64, 200)
RED = (255, 64, 64)
RED_DARK = (200, 32, 32)
GREEN = (64, 255, 128)
GREEN_DARK = (32, 200, 64)
YELLOW = (255, 220, 64)
PURPLE = (128, 64, 255)
CYAN = (64, 255, 255)

@dataclass
class HandData:
    x: int = 400
    y: int = 400
    pinching: bool = False
    active: bool = False
    hands_count: int = 0

class HandTracker:
    def __init__(self):
        self.hand_data = HandData()
        self.connection = None
        self.running = False
        self.thread = None
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _tracking_loop(self):
        """Separate thread for hand tracking"""
        print("Starting hand tracking thread...")
        
        listener = TrackingListener(self.hand_data)
        connection = leap.Connection()
        connection.add_listener(listener)
        
        try:
            with connection.open():
                connection.set_tracking_mode(leap.TrackingMode.Desktop)
                print("Hand tracking thread connected")
                
                while self.running:
                    time.sleep(0.01)
                    
        except Exception as e:
            print(f"Hand tracking error: {e}")
        
        print("Hand tracking thread stopped")

class TrackingListener(leap.Listener):
    def __init__(self, hand_data):
        self.hand_data = hand_data
        self.last_update = 0
        
    def on_connection_event(self, event):
        print("Connected to Ultra Leap (threaded)")
        
    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()
        print(f"Found device {info.serial} (threaded)")
        
    def on_tracking_event(self, event):
        current_time = time.time()
        
        self.hand_data.hands_count = len(event.hands)
        self.hand_data.active = True
        
        if event.hands:
            hand = event.hands[0]
            palm = hand.palm
            
            # Convert coordinates
            self.hand_data.x = int((palm.position.x + 200) * (WINDOW_WIDTH / 400))
            self.hand_data.y = int((400 - palm.position.y) * (WINDOW_HEIGHT / 400))
            
            # Keep within bounds
            self.hand_data.x = max(0, min(WINDOW_WIDTH, self.hand_data.x))
            self.hand_data.y = max(0, min(WINDOW_HEIGHT, self.hand_data.y))
            
            # Detect pinch
            if len(hand.digits) >= 2:
                thumb_tip = hand.digits[0].distal.next_joint
                index_tip = hand.digits[1].distal.next_joint
                distance = ((thumb_tip.x - index_tip.x) ** 2 + 
                           (thumb_tip.y - index_tip.y) ** 2 + 
                           (thumb_tip.z - index_tip.z) ** 2) ** 0.5
                self.hand_data.pinching = distance < 30
            else:
                self.hand_data.pinching = False
        else:
            self.hand_data.pinching = False
            
        self.last_update = current_time

class AnimatedButton:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        self.animation_progress = 0
        self.hand_hover_time = 0
        self.hand_activated = False
        
    def update(self, mouse_pos, hand_pos=None, hand_pinching=False):
        was_hovered = self.hovered
        
        # Check mouse hover
        mouse_hovered = self.rect.collidepoint(mouse_pos)
        
        # Check hand hover
        hand_hovered = False
        if hand_pos:
            hand_hovered = self.rect.collidepoint(hand_pos)
        
        self.hovered = mouse_hovered or hand_hovered
        
        # Hand activation logic (hover for 1 second or pinch)
        if hand_hovered:
            if hand_pinching:
                self.hand_activated = True
            else:
                self.hand_hover_time += 0.016  # ~60fps
                if self.hand_hover_time >= 1.0:  # 1 second hover
                    self.hand_activated = True
        else:
            self.hand_hover_time = 0
            self.hand_activated = False
        
        # Smooth color transition
        if self.hovered and self.animation_progress < 1:
            self.animation_progress = min(1, self.animation_progress + 0.1)
        elif not self.hovered and self.animation_progress > 0:
            self.animation_progress = max(0, self.animation_progress - 0.1)
            
        # Interpolate colors
        r = self.color[0] + (self.hover_color[0] - self.color[0]) * self.animation_progress
        g = self.color[1] + (self.hover_color[1] - self.color[1]) * self.animation_progress
        b = self.color[2] + (self.hover_color[2] - self.color[2]) * self.animation_progress
        self.current_color = (int(r), int(g), int(b))
    
    def draw(self, screen, font):
        # Draw button with rounded corners
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        
        # Draw hover progress indicator for hand tracking
        if self.hand_hover_time > 0 and self.hand_hover_time < 1.0:
            progress_width = int((self.rect.width - 4) * self.hand_hover_time)
            progress_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, progress_width, 4)
            pygame.draw.rect(screen, YELLOW, progress_rect)
        
        # Draw text
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed
    
    def is_hand_activated(self):
        if self.hand_activated:
            self.hand_activated = False  # Reset after activation
            self.hand_hover_time = 0
            return True
        return False

class TicTacToeGame:
    def __init__(self):
        self.fullscreen = True
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Hand Tracking Tic Tac Toe")
        self.clock = pygame.time.Clock()
        
        # Enhanced fonts
        self.font_title = pygame.font.Font(None, 64)
        self.font_large = pygame.font.Font(None, 120)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_line = None
        
        # Visual effects
        self.cell_animations = [[0 for _ in range(3)] for _ in range(3)]
        self.background_particles = []
        self.time_elapsed = 0
        
        # Logo & Background
        self.logo1_surface = None
        self.logo2_surface = None
        self.background_image = None
        self.use_image_background = True  # Set to False to use gradient background
        self.load_logos()
        self.load_background()
        
        # UI Elements
        self.reset_button = AnimatedButton(
            WINDOW_WIDTH - 140, 20, 120, 50, "🔄 Reset", PURPLE, (160, 96, 255)
        )
        
        self.fullscreen_button = AnimatedButton(
            WINDOW_WIDTH - 280, 20, 130, 50, "🖥️ Fullscreen", GREEN_DARK, GREEN
        )
        
        self.background_button = AnimatedButton(
            WINDOW_WIDTH - 430, 20, 140, 50, "🎨 Background", BLUE_DARK, BLUE
        )
        
        self.background_button = AnimatedButton(
            WINDOW_WIDTH - 430, 20, 140, 50, "🎨 Background", BLUE_DARK, BLUE
        )
        
        # Hand tracking
        self.hand_tracker = HandTracker()
        self.last_pinch = False
        
        # Initialize particles
        self.init_particles()
        
    def load_logos(self):
        """Load PNG logo images"""
        # Logo filenames - you can change these to match your PNG files
        logo1_filename = "3-stripes.png"  # Change this to your first logo filename
        logo2_filename = "3-foil.png"  # Change this to your second logo filename
        
        # Target logo size
        logo_size = (80, 80)  # Width, Height
        
        try:
            # Load first logo
            if os.path.exists(logo1_filename):
                self.logo1_surface = pygame.image.load(logo1_filename).convert_alpha()
                # Scale to desired size while maintaining aspect ratio
                self.logo1_surface = self.scale_image_maintain_aspect(self.logo1_surface, logo_size)
                print(f"✅ Logo 1 loaded: {logo1_filename}")
            else:
                print(f"❌ Logo 1 not found: {logo1_filename} - Creating default logo")
                self.logo1_surface = self.create_default_logo(logo_size, CYAN)
                
            # Load second logo
            if os.path.exists(logo2_filename):
                self.logo2_surface = pygame.image.load(logo2_filename).convert_alpha()
                # Scale to desired size while maintaining aspect ratio
                self.logo2_surface = self.scale_image_maintain_aspect(self.logo2_surface, logo_size)
                print(f"✅ Logo 2 loaded: {logo2_filename}")
            else:
                print(f"❌ Logo 2 not found: {logo2_filename} - Creating default logo")
                self.logo2_surface = self.create_default_logo(logo_size, PURPLE)
                
        except pygame.error as e:
            print(f"❌ Error loading logos: {e}")
            # Create default logos as fallback
            self.logo1_surface = self.create_default_logo(logo_size, CYAN)
            self.logo2_surface = self.create_default_logo(logo_size, PURPLE)
    
    def scale_image_maintain_aspect(self, image, target_size):
        """Scale image while maintaining aspect ratio"""
        original_width, original_height = image.get_size()
        target_width, target_height = target_size
        
        # Calculate scaling factor to fit within target size
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)  # Use smaller scale to fit within bounds
        
        # Calculate new size
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        return pygame.transform.smoothscale(image, (new_width, new_height))
    
    def create_default_logo(self, size, color):
        """Create a default logo if PNG file is not found"""
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        center_x, center_y = width // 2, height // 2
        
        # Draw outer circle with glow effect
        for i in range(3):
            alpha = 255 - i * 80
            glow_surface = pygame.Surface(size, pygame.SRCALPHA)
            radius = center_x - i * 3
            pygame.draw.circle(glow_surface, (*color, alpha), (center_x, center_y), radius)
            surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw inner design
        grid_size = width // 3
        cell_size = grid_size // 3
        start_x = center_x - grid_size // 2
        start_y = center_y - grid_size // 2
        
        # Mini grid
        for i in range(4):
            # Vertical lines
            x = start_x + i * cell_size
            pygame.draw.line(surface, WHITE, (x, start_y), (x, start_y + grid_size), 2)
            # Horizontal lines
            y = start_y + i * cell_size
            pygame.draw.line(surface, WHITE, (start_x, y), (start_x + grid_size, y), 2)
        
    def draw_gradient_background(self):
        """Draw animated gradient background (fallback when no image)"""
        current_width = self.screen.get_width()
        current_height = self.screen.get_height()
        
        for y in range(current_height):
            ratio = y / current_height
            wave = math.sin(self.time_elapsed * 2 + ratio * 4) * 10
            
            r = int(20 + wave)
            g = int(20 + wave)
            b = int(25 + wave * 1.5)
            
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(self.screen, color, (0, y), (current_width, y))
    
    def toggle_background_mode(self):
        """Toggle between image background and gradient background"""
        if self.background_image:
            self.use_image_background = not self.use_image_background
            mode = "Image" if self.use_image_background else "Gradient"
            print(f"Background mode switched to: {mode}")
        else:
            print("No background image available - staying in gradient mode")
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Get display info for fullscreen
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            
            # Update button positions for fullscreen
            self.reset_button.rect.x = info.current_w - 140
            self.fullscreen_button.rect.x = info.current_w - 280
            self.background_button.rect.x = info.current_w - 430
            self.fullscreen_button.text = "🪟 Windowed"
            
        else:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            
            # Reset button positions for windowed mode
            self.reset_button.rect.x = WINDOW_WIDTH - 140
            self.fullscreen_button.rect.x = WINDOW_WIDTH - 280
            self.background_button.rect.x = WINDOW_WIDTH - 430
            self.fullscreen_button.text = "🖥️ Fullscreen"
        
    def init_particles(self):
        """Create background particles for visual flair"""
        for _ in range(20):
            self.background_particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150)
            })
        
    def reset_game(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_line = None
        self.cell_animations = [[0 for _ in range(3)] for _ in range(3)]
        
    def get_grid_position(self, x, y):
        """Convert screen coordinates to grid position"""
        if (x >= GRID_OFFSET_X and x < GRID_OFFSET_X + GRID_SIZE and
            y >= GRID_OFFSET_Y and y < GRID_OFFSET_Y + GRID_SIZE):
            
            col = (x - GRID_OFFSET_X) // CELL_SIZE
            row = (y - GRID_OFFSET_Y) // CELL_SIZE
            
            if 0 <= row < 3 and 0 <= col < 3:
                return row, col
                
        return None, None
    
    def make_move(self, row, col):
        if (0 <= row < 3 and 0 <= col < 3 and 
            self.board[row][col] == '' and not self.game_over):
            
            self.board[row][col] = self.current_player
            self.cell_animations[row][col] = 1.0  # Start animation
            self.check_winner()
            
            if not self.game_over:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def check_winner(self):
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
    
    def handle_input(self):
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
        
        # Update UI elements with hand tracking
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        
        self.reset_button.update(mouse_pos, hand_pos, hand_data.pinching)
        self.fullscreen_button.update(mouse_pos, hand_pos, hand_data.pinching)
        self.background_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Check for hand activation
        if self.reset_button.is_hand_activated():
            self.reset_game()
            print("Game reset by hand gesture!")
            
        if self.fullscreen_button.is_hand_activated():
            self.toggle_fullscreen()
            print("Fullscreen toggled by hand gesture!")
            
        if self.background_button.is_hand_activated():
            self.toggle_background_mode()
            print("Background mode toggled by hand gesture!")
    
    def load_background(self):
        """Load background image"""
        background_filename = "background.png"  # Change this to your background image filename
        # Supported formats: .png, .jpg, .jpeg, .bmp, .gif
        
        # Try different common background filenames
        possible_backgrounds = [
            "background.png", "background.jpg", "background.jpeg",
            "bata-putih.jpg", "bg.jpg", "bg.jpeg",
            "wallpaper.png", "wallpaper.jpg", "wallpaper.jpeg"
        ]
        
        background_loaded = False
        
        for bg_file in possible_backgrounds:
            if os.path.exists(bg_file):
                try:
                    self.background_image = pygame.image.load(bg_file).convert()
                    print(f"✅ Background loaded: {bg_file}")
                    background_loaded = True
                    break
                except pygame.error as e:
                    print(f"❌ Error loading background {bg_file}: {e}")
                    continue
        
        if not background_loaded:
            print("ℹ️ No background image found - using gradient background")
            self.use_image_background = False
            self.background_image = None
    
    def draw_background(self):
        """Draw background - either image or gradient"""
        current_width = self.screen.get_width()
        current_height = self.screen.get_height()
        
        if self.use_image_background and self.background_image:
            # Scale background image to fit screen
            scaled_bg = pygame.transform.scale(self.background_image, (current_width, current_height))
            
            # Draw background image
            self.screen.blit(scaled_bg, (0, 0))
            
            # Optional: Add dark overlay for better text visibility
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(120)  # Adjust transparency (0-255)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
        else:
            # Draw animated gradient background (fallback)
            self.draw_gradient_background()
    
    def update_particles(self):
        """Update background particles"""
        current_width = self.screen.get_width()
        current_height = self.screen.get_height()
        
        for particle in self.background_particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = current_width
            elif particle['x'] > current_width:
                particle['x'] = 0
                
            if particle['y'] < 0:
                particle['y'] = current_height
            elif particle['y'] > current_height:
                particle['y'] = 0
    
    def draw_particles(self):
        """Draw background particles"""
        for particle in self.background_particles:
            # Create surface for alpha blending
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surface.set_alpha(particle['alpha'])
            pygame.draw.circle(particle_surface, CYAN, 
                             (particle['size'], particle['size']), particle['size'])
            self.screen.blit(particle_surface, 
                           (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def draw_enhanced_grid(self):
        """Draw grid with glowing effects"""
        # Draw grid lines with glow
        for i in range(4):
            # Vertical lines
            x = GRID_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(self.screen, CYAN, (x, GRID_OFFSET_Y), 
                           (x, GRID_OFFSET_Y + GRID_SIZE), 4)
            
            # Horizontal lines
            y = GRID_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(self.screen, CYAN, (GRID_OFFSET_X, y), 
                           (GRID_OFFSET_X + GRID_SIZE, y), 4)
        
        # Draw cell backgrounds
        for row in range(3):
            for col in range(3):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                
                # Animated cell highlight
                if self.cell_animations[row][col] > 0:
                    alpha = int(self.cell_animations[row][col] * 100)
                    highlight_surface = pygame.Surface((CELL_SIZE - 8, CELL_SIZE - 8))
                    highlight_surface.set_alpha(alpha)
                    
                    if self.board[row][col] == 'X':
                        highlight_surface.fill(RED)
                    else:
                        highlight_surface.fill(BLUE)
                    
                    self.screen.blit(highlight_surface, (x + 4, y + 4))
                    self.cell_animations[row][col] *= 0.95  # Fade out
    
    def draw_symbols(self):
        """Draw X's and O's with enhanced graphics"""
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != '':
                    center_x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
                    center_y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
                    
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
        """Draw winning line animation"""
        if self.win_line and self.winner != 'Draw':
            line_type, index = self.win_line
            
            # Calculate line positions
            if line_type == 'row':
                start_x = GRID_OFFSET_X + 20
                end_x = GRID_OFFSET_X + GRID_SIZE - 20
                start_y = end_y = GRID_OFFSET_Y + index * CELL_SIZE + CELL_SIZE // 2
            elif line_type == 'col':
                start_x = end_x = GRID_OFFSET_X + index * CELL_SIZE + CELL_SIZE // 2
                start_y = GRID_OFFSET_Y + 20
                end_y = GRID_OFFSET_Y + GRID_SIZE - 20
            elif line_type == 'diag':
                if index == 0:  # Top-left to bottom-right
                    start_x, start_y = GRID_OFFSET_X + 20, GRID_OFFSET_Y + 20
                    end_x, end_y = GRID_OFFSET_X + GRID_SIZE - 20, GRID_OFFSET_Y + GRID_SIZE - 20
                else:  # Top-right to bottom-left
                    start_x, start_y = GRID_OFFSET_X + GRID_SIZE - 20, GRID_OFFSET_Y + 20
                    end_x, end_y = GRID_OFFSET_X + 20, GRID_OFFSET_Y + GRID_SIZE - 20
            
            # Draw glowing win line
            pygame.draw.line(self.screen, YELLOW, (start_x, start_y), (end_x, end_y), 8)
            pygame.draw.line(self.screen, WHITE, (start_x, start_y), (end_x, end_y), 4)
    
    def render(self):
        self.time_elapsed += 0.016  # ~60fps
        
        # Draw background (image or gradient)
        self.draw_background()
        
        # Update and draw particles
        self.update_particles()
        self.draw_particles()
        
        # Draw logos
        logo1_y = 40  # Logo 1 diturunkan dari 20 ke 40
        logo2_y = 20  # Logo 2 tetap di posisi original
        logo_spacing = 100  # Space between logos
        
        if self.logo1_surface:
            logo1_x = 30
            self.screen.blit(self.logo1_surface, (logo1_x, logo1_y))
            
        if self.logo2_surface:
            logo2_x = 30 + logo_spacing
            self.screen.blit(self.logo2_surface, (logo2_x, logo2_y))
        
        # Draw title with logo spacing - positioned after both logos
        title_text = self.font_title.render("TIC TAC TOE", True, WHITE)
        title_x = 250  # Positioned after both logos
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
            x = GRID_OFFSET_X + col * CELL_SIZE
            y = GRID_OFFSET_Y + row * CELL_SIZE
            
            highlight_color = YELLOW if hand_data.pinching else GREEN
            alpha = int(150 + math.sin(self.time_elapsed * 8) * 50)
            
            highlight_surface = pygame.Surface((CELL_SIZE - 10, CELL_SIZE - 10))
            highlight_surface.set_alpha(alpha)
            highlight_surface.fill(highlight_color)
            self.screen.blit(highlight_surface, (x + 5, y + 5))
        
        # Draw win line
        self.draw_win_line()
        
        # Draw hand indicator with pulse
        if hand_data.active and hand_data.hands_count > 0:
            pulse = math.sin(self.time_elapsed * 6) * 3 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
        
        # Draw game info panel
        panel_y = GRID_OFFSET_Y + GRID_SIZE + 30
        current_player_text = self.font_medium.render(f"Current Player: {self.current_player}", True, WHITE)
        panel_center_x = self.screen.get_width() // 2
        text_rect = current_player_text.get_rect(center=(panel_center_x, panel_y))
        self.screen.blit(current_player_text, text_rect)
        
        # Status with enhanced styling
        if self.game_over:
            if self.winner == 'Draw':
                status = "🤝 It's a Draw! 🤝"
                status_color = YELLOW
            else:
                status = f"🎉 Player {self.winner} Wins! 🎉"
                status_color = RED if self.winner == 'X' else BLUE
        else:
            if hand_data.active and hand_data.hands_count > 0:
                status = f"✋ Hand Tracking: {hand_data.hands_count} hands detected"
                status_color = GREEN
            else:
                status = "🖱️ Using mouse (no hand tracking)"
                status_color = LIGHT_GRAY
                
        status_text = self.font_medium.render(status, True, status_color)
        status_rect = status_text.get_rect(center=(panel_center_x, panel_y + 40))
        self.screen.blit(status_text, status_rect)
        
        # Draw buttons
        self.reset_button.draw(self.screen, self.font_small)
        self.fullscreen_button.draw(self.screen, self.font_small)
        self.background_button.draw(self.screen, self.font_small)
        
        # Instructions
        instructions = [
            "Move hand over cell and PINCH to place mark",
            "Hover over buttons for 1 sec or PINCH to activate",
            "Mouse click also works | F11: Fullscreen | B: Toggle BG | ESC: Exit"
        ]
        instruction_y = self.screen.get_height() - 80
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(panel_center_x, instruction_y + i * 25))
            self.screen.blit(text, text_rect)
    
    def run(self):
        print("Starting Enhanced Tic Tac Toe...")
        
        # Start hand tracking in separate thread
        self.hand_tracker.start()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_b:
                        self.toggle_background_mode()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check button clicks
                    if self.reset_button.is_clicked(event.pos, True):
                        self.reset_game()
                    elif self.fullscreen_button.is_clicked(event.pos, True):
                        self.toggle_fullscreen()
                    elif self.background_button.is_clicked(event.pos, True):
                        self.toggle_background_mode()
                    else:
                        # Mouse fallback for game moves
                        row, col = self.get_grid_position(event.pos[0], event.pos[1])
                        if row is not None and col is not None:
                            self.make_move(row, col)
            
            self.handle_input()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)  
        
        self.hand_tracker.stop()
        pygame.quit()
        sys.exit()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check button clicks
                    if self.reset_button.is_clicked(event.pos, True):
                        self.reset_game()
                    else:
                        # Mouse fallback for game moves
                        row, col = self.get_grid_position(event.pos[0], event.pos[1])
                        if row is not None and col is not None:
                            self.make_move(row, col)
            
            self.handle_input()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)  
        
        self.hand_tracker.stop()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()