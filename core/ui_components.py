"""
Reusable UI components for all games
Extracted from tic_tac_toe.py for modularity
"""

import pygame
import random
import math
import os
from .constants import *

# Import OpenCV untuk video support
try:
    import cv2
    CV2_AVAILABLE = True
    print("OpenCV loaded - video background support enabled")
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not available - video background disabled")


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
                if self.hand_hover_time >= HAND_HOVER_TIME_THRESHOLD:
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
        if self.hand_hover_time > 0 and self.hand_hover_time < HAND_HOVER_TIME_THRESHOLD:
            progress_width = int((self.rect.width - 4) * (self.hand_hover_time / HAND_HOVER_TIME_THRESHOLD))
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


class ParticleSystem:
    def __init__(self, particle_count=20):
        self.particles = []
        self.init_particles(particle_count)
        
    def init_particles(self, count):
        """Create background particles for visual flair"""
        for _ in range(count):
            self.particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150)
            })
    
    def update(self, screen_width=WINDOW_WIDTH, screen_height=WINDOW_HEIGHT):
        """Update particle positions"""
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = screen_width
            elif particle['x'] > screen_width:
                particle['x'] = 0
                
            if particle['y'] < 0:
                particle['y'] = screen_height
            elif particle['y'] > screen_height:
                particle['y'] = 0
    
    def draw(self, screen):
        """Draw particles with alpha blending"""
        for particle in self.particles:
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            particle_surface.set_alpha(particle['alpha'])
            pygame.draw.circle(particle_surface, CYAN, 
                             (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surface, 
                       (particle['x'] - particle['size'], particle['y'] - particle['size']))


class VideoBackgroundManager:
    def __init__(self):
        self.background_image = None
        self.video_cap = None
        self.video_surface = None
        self.background_mode = "gradient"  # "gradient", "image", "video"
        self.time_elapsed = 0
        self.frame_delay = 0
        self.video_fps = 30  # Default FPS
        
        self.load_background_assets()
    
    def load_background_assets(self):
        """Load semua background assets: image dan video"""
        # Load background image
        self.load_background_image()
        
        # Load background video jika OpenCV tersedia
        if CV2_AVAILABLE:
            self.load_background_video()
        
        # Set default mode berdasarkan asset yang tersedia
        if self.video_cap is not None:
            self.background_mode = "video"
            print("Video background loaded - using video mode")
        elif self.background_image is not None:
            self.background_mode = "image" 
            print("Image background loaded - using image mode")
        else:
            self.background_mode = "gradient"
            print("Using gradient background mode")
    
    def load_background_image(self):
        """Load background image dari nama file umum"""
        possible_backgrounds = [
            "background.png", "background.jpg", "background.jpeg",
            "bata-3.jpg", "bg.jpg", "bg.jpeg",
            "wallpaper.png", "wallpaper.jpg", "wallpaper.jpeg"
        ]
        
        for bg_file in possible_backgrounds:
            if os.path.exists(bg_file):
                try:
                    self.background_image = pygame.image.load(bg_file).convert()
                    print(f"Background image loaded: {bg_file}")
                    break
                except pygame.error as e:
                    print(f"Error loading background {bg_file}: {e}")
                    continue
    
    def load_background_video(self):
        """Load background video menggunakan OpenCV"""
        video_filename = "white.gif"
        
        if os.path.exists(video_filename):
            try:
                self.video_cap = cv2.VideoCapture(video_filename)
                
                if self.video_cap.isOpened():
                    # Get video properties
                    self.video_fps = int(self.video_cap.get(cv2.CAP_PROP_FPS))
                    frame_count = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    print(f"Video loaded: {video_filename}")
                    print(f"Video FPS: {self.video_fps}, Total frames: {frame_count}")
                else:
                    print(f"Cannot open video file: {video_filename}")
                    self.video_cap = None
                    
            except Exception as e:
                print(f"Error loading video {video_filename}: {e}")
                self.video_cap = None
        else:
            print(f"Video file not found: {video_filename}")
    
    def get_current_video_frame(self, screen_width, screen_height):
        """Get current video frame dan scale sesuai screen size"""
        if not self.video_cap or not CV2_AVAILABLE:
            return None
        
        # Calculate frame timing
        target_frame_delay = 1000 // self.video_fps  # milliseconds
        current_time = pygame.time.get_ticks()
        
        if current_time - self.frame_delay >= target_frame_delay:
            ret, frame = self.video_cap.read()
            
            if not ret:  # End of video, loop back
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.video_cap.read()
            
            if ret:
                # Convert BGR ke RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame untuk match screen resolution
                frame = cv2.resize(frame, (screen_width, screen_height))
                
                # Convert ke pygame surface
                frame = frame.swapaxes(0, 1)  # Transpose untuk pygame
                self.video_surface = pygame.surfarray.make_surface(frame)
                
                self.frame_delay = current_time
        
        return self.video_surface
    
    def toggle_background_mode(self):
        """Cycle through available background modes"""
        modes = []
        
        if self.video_cap and CV2_AVAILABLE:
            modes.append("video")
        if self.background_image:
            modes.append("image")
        modes.append("gradient")  # Always available
        
        if len(modes) > 1:
            current_index = modes.index(self.background_mode)
            next_index = (current_index + 1) % len(modes)
            self.background_mode = modes[next_index]
            
            print(f"Background mode switched to: {self.background_mode}")
        else:
            print("Only one background mode available")
    
    def draw_gradient_background(self, screen):
        """Draw animated gradient background"""
        current_width = screen.get_width()
        current_height = screen.get_height()
        
        for y in range(current_height):
            ratio = y / current_height
            wave = math.sin(self.time_elapsed * 2 + ratio * 4) * 10
            
            r = int(20 + wave)
            g = int(20 + wave)
            b = int(25 + wave * 1.5)
            
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(screen, color, (0, y), (current_width, y))
    
    def draw(self, screen):
        """Draw background berdasarkan mode yang aktif"""
        self.time_elapsed += 0.016  # ~60fps
        
        current_width = screen.get_width()
        current_height = screen.get_height()
        
        if self.background_mode == "video" and self.video_cap and CV2_AVAILABLE:
            # Draw video background
            video_frame = self.get_current_video_frame(current_width, current_height)
            
            if video_frame:
                screen.blit(video_frame, (0, 0))
                
                # Add slight dark overlay untuk text visibility yang lebih baik
                overlay = pygame.Surface((current_width, current_height))
                overlay.set_alpha(60)  # Lebih transparan dari image overlay
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
            else:
                # Fallback ke gradient jika video frame tidak tersedia
                self.draw_gradient_background(screen)
                
        elif self.background_mode == "image" and self.background_image:
            # Draw image background
            scaled_bg = pygame.transform.scale(self.background_image, (current_width, current_height))
            screen.blit(scaled_bg, (0, 0))
            
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(120)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
        else:
            # Draw gradient background
            self.draw_gradient_background(screen)
    
    def cleanup(self):
        """Cleanup resources saat aplikasi ditutup"""
        if self.video_cap:
            self.video_cap.release()
            print("Video resources cleaned up")


# Alias untuk backward compatibility
BackgroundManager = VideoBackgroundManager


class LogoManager:
    def __init__(self):
        self.logo1_surface = None
        self.logo2_surface = None
        self.load_logos()
    
    def load_logos(self):
        """Load PNG logo images"""
        logo1_filename = ""
        logo2_filename = ""
        logo_size = (90, 90)
        
        try:
            # Load first logo
            if os.path.exists(logo1_filename):
                self.logo1_surface = pygame.image.load(logo1_filename).convert_alpha()
                self.logo1_surface = self.scale_image_maintain_aspect(self.logo1_surface, logo_size)
                print(f"Logo 1 loaded: {logo1_filename}")
            # else:
            #     print(f"Logo 1 not found: {logo1_filename} - Creating default logo")
            #     self.logo1_surface = self.create_default_logo(logo_size, CYAN)
                
            # Load second logo
            if os.path.exists(logo2_filename):
                self.logo2_surface = pygame.image.load(logo2_filename).convert_alpha()
                self.logo2_surface = self.scale_image_maintain_aspect(self.logo2_surface, logo_size)
                print(f"Logo 2 loaded: {logo2_filename}")
            # else:
            #     print(f"Logo 2 not found: {logo2_filename} - Creating default logo")
            #     self.logo2_surface = self.create_default_logo(logo_size, PURPLE)
                
        except pygame.error as e:
            print(f"Error loading logos: {e}")
            self.logo1_surface = self.create_default_logo(logo_size, CYAN)
            self.logo2_surface = self.create_default_logo(logo_size, PURPLE)
    
    def scale_image_maintain_aspect(self, image, target_size):
        """Scale image while maintaining aspect ratio"""
        original_width, original_height = image.get_size()
        target_width, target_height = target_size
        
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)
        
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
        
        # Draw inner design (mini grid)
        grid_size = width // 3
        cell_size = grid_size // 3
        start_x = center_x - grid_size // 2
        start_y = center_y - grid_size // 2
        
        for i in range(4):
            x = start_x + i * cell_size
            pygame.draw.line(surface, WHITE, (x, start_y), (x, start_y + grid_size), 2)
            y = start_y + i * cell_size
            pygame.draw.line(surface, WHITE, (start_x, y), (start_x + grid_size, y), 2)
        
        return surface
    
    def draw(self, screen, x=30, y_offset1=37, y_offset2=20):
        """Draw both logos"""
        if self.logo1_surface:
            screen.blit(self.logo1_surface, (x, y_offset1))
            
        if self.logo2_surface:
            logo2_x = x + 100  # Space between logos
            screen.blit(self.logo2_surface, (logo2_x, y_offset2))