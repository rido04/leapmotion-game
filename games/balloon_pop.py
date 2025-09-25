# games/balloon_pop.py -  VERSION
"""
Balloon Pop Game using hand tracking
Pop balloons as they float up from the bottom
: Better pop animations, optimized spawn zones, improved performance
"""

import pygame
import random
import math
import time
from .base_game import BaseGame
from core import *


class PopEffect:
    """Separate class for enhanced pop effects - OPTIMIZED"""
    def __init__(self, x, y, balloon_color, balloon_size):
        self.x = x
        self.y = y
        self.time = 0
        self.duration = 0.8
        self.balloon_color = balloon_color
        self.size_multiplier = {'small': 0.8, 'medium': 1.0, 'large': 1.2}.get(balloon_size, 1.0)
        
        # Create particle bursts
        self.particles = []
        particle_count = 8  # Fixed count for performance
        for i in range(particle_count):
            angle = (i / particle_count) * math.pi * 2
            speed = random.uniform(60, 120) * self.size_multiplier
            self.particles.append({
                'start_x': x,
                'start_y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - random.uniform(20, 40),  # Slight upward bias
                'color': self.get_particle_color(),
                'size': random.randint(3, 6),
                'life': 1.0
            })
        
        # Shockwave effect
        self.shockwave_radius = 0
        self.max_shockwave_radius = 60 * self.size_multiplier
        
        # Star burst effect
        self.stars = []
        for i in range(5):
            angle = (i / 5) * math.pi * 2 + random.uniform(-0.3, 0.3)
            distance = random.uniform(20, 40) * self.size_multiplier
            self.stars.append({
                'x': x + math.cos(angle) * distance,
                'y': y + math.sin(angle) * distance,
                'size': random.randint(4, 8),
                'rotation': 0,
                'color': (255, 255, 100)
            })
    
    def get_particle_color(self):
        """Get appropriate particle color based on balloon color"""
        color_map = {
            'orange': [(255, 200, 100), (255, 150, 0), (255, 100, 0)],
            'red': [(255, 100, 100), (255, 50, 50), (200, 0, 0)],
            'blue': [(100, 150, 255), (50, 100, 255), (0, 50, 200)],
            'cyan': [(100, 255, 255), (0, 200, 255), (0, 150, 200)],
            'pink': [(255, 150, 200), (255, 100, 150), (200, 50, 100)],
            'gray': [(200, 200, 200), (150, 150, 150), (100, 100, 100)]
        }
        colors = color_map.get(self.balloon_color, [(255, 255, 255), (200, 200, 200)])
        return random.choice(colors)
    
    def update(self, dt):
        """Update pop effect animation"""
        self.time += dt
        progress = self.time / self.duration
        
        if progress >= 1.0:
            return False
        
        # Update particles
        for particle in self.particles:
            particle['start_x'] += particle['vx'] * dt
            particle['start_y'] += particle['vy'] * dt
            particle['vy'] += 150 * dt  # Gravity
            particle['life'] = 1.0 - (progress * 1.5)  # Fade out
        
        # Update shockwave
        self.shockwave_radius = self.max_shockwave_radius * min(1.0, progress * 3)
        
        # Update stars
        for star in self.stars:
            star['rotation'] += dt * 360  # Rotate stars
        
        return True
    
    def draw(self, screen):
        """Draw enhanced pop effect"""
        progress = self.time / self.duration
        
        # Draw shockwave (ring effect)
        if progress < 0.3:
            shockwave_alpha = int(255 * (1 - progress / 0.3))
            if self.shockwave_radius > 0 and shockwave_alpha > 0:
                # Create temporary surface for alpha blending
                shockwave_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
                pygame.draw.circle(shockwave_surface, (255, 255, 255, shockwave_alpha//2), 
                                 (100, 100), int(self.shockwave_radius), 3)
                screen.blit(shockwave_surface, 
                           (self.x - 100, self.y - 100), 
                           special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = max(0, int(255 * particle['life']))
                size = max(1, int(particle['size'] * particle['life']))
                
                # Simple particle with fade
                color_with_alpha = particle['color'] + (alpha,)
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['start_x']), int(particle['start_y'])), size)
        
        # Draw rotating stars
        if progress < 0.5:
            star_alpha = 1.0 - (progress / 0.5)
            for star in self.stars:
                star_size = int(star['size'] * star_alpha)
                if star_size > 0:
                    self.draw_star(screen, int(star['x']), int(star['y']), 
                                 star_size, star['rotation'], star['color'])
    
    def draw_star(self, screen, x, y, size, rotation, color):
        """Draw a simple star shape"""
        # Simple 4-point star (plus shape) for performance
        points = []
        for i in range(4):
            angle = math.radians(rotation + i * 90)
            point_x = x + math.cos(angle) * size
            point_y = y + math.sin(angle) * size
            points.append((int(point_x), int(point_y)))
            
            # Add inner points for star shape
            inner_angle = math.radians(rotation + i * 90 + 45)
            inner_size = size * 0.4
            inner_x = x + math.cos(inner_angle) * inner_size
            inner_y = y + math.sin(inner_angle) * inner_size
            points.append((int(inner_x), int(inner_y)))
        
        if len(points) >= 6:
            pygame.draw.polygon(screen, color, points[:6])


class Balloon:
    """Individual balloon object - """
    def __init__(self, x, y, balloon_images_dict, color_name, screen_width, screen_height):
        # Pre-scaled images dictionary (small, medium, large, hover)
        self.images = balloon_images_dict[color_name]
        self.color_name = color_name
        
        # Store screen dimensions for boundary checking
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Movement properties with slight variation
        base_speed = random.uniform(1.2, 2.8)
        self.speed_y = base_speed
        self.speed_x = random.uniform(-0.3, 0.3)  # Reduced horizontal drift
        self.float_amplitude = random.uniform(8, 15)  # Reduced floating
        self.float_frequency = random.uniform(0.8, 1.2)
        self.initial_x = x
        
        # Visual properties
        self.scale_type = random.choice(['small', 'medium', 'large'])
        self.current_image = self.images[self.scale_type]
        self.rect = self.current_image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        
        # Enhanced animation properties
        self.rotation = 0
        self.rotation_speed = random.uniform(-1.5, 1.5)  # Slower rotation
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.bounce_amplitude = random.uniform(0.5, 1.5)  # Vertical bounce
        self.bounce_frequency = random.uniform(2, 4)
        
        # State
        self.popped = False
        self.pop_animation = 0.0
        self.is_hovering = False
        self.hover_scale = 1.0
        self.target_hover_scale = 1.0
        self.glow_animation = 0
        self.rotated_image = None
        self.rotation_cache_angle = 0
        
        # Enhanced visual feedback
        self.pulse_animation = random.uniform(0, math.pi * 2)  # Random start phase
        self.shine_offset = random.uniform(0, 1000)
        
        # Score value based on speed and size (enhanced calculation)
        size_multiplier = {'small': 1.5, 'medium': 1.0, 'large': 0.7}[self.scale_type]
        speed_bonus = (self.speed_y - 1.2) / 1.6  # Normalized speed bonus
        self.points = int(40 + speed_bonus * 60 * size_multiplier)
        
        # Collision optimization
        self.collision_radius = {'small': 25, 'medium': 35, 'large': 45}[self.scale_type]
    
    def update(self, dt, time_elapsed):
        """Update balloon position and animations - """
        if self.popped:
            self.pop_animation += dt * 4  # Slightly slower for better visibility
            return self.pop_animation < 1.0
        
        # Enhanced movement with bounce
        old_y = self.rect.y
        vertical_bounce = math.sin(time_elapsed * self.bounce_frequency + self.bob_offset) * self.bounce_amplitude
        self.rect.y -= self.speed_y + vertical_bounce * 0.1
        
        # Smoother floating motion
        float_offset = math.sin(time_elapsed * self.float_frequency + self.bob_offset) * self.float_amplitude
        wind_effect = math.sin(time_elapsed * 0.3) * 5  # Gentle wind
        self.rect.centerx = self.initial_x + self.speed_x * time_elapsed + float_offset + wind_effect
        
        # Keep balloon within safe bounds (not too close to edges)
        margin = 80  # Increased margin for better hand tracking
        if self.rect.centerx < margin:
            self.rect.centerx = margin
        elif self.rect.centerx > self.screen_width - margin:
            self.rect.centerx = self.screen_width - margin
        
        # Smooth rotation with cache optimization
        new_rotation = self.rotation + self.rotation_speed * dt
        if abs(new_rotation - self.rotation_cache_angle) > 8:
            self.rotation = new_rotation
            if abs(self.rotation) > 2:
                self.rotated_image = pygame.transform.rotate(self.current_image, self.rotation)
                self.rotation_cache_angle = self.rotation
            else:
                self.rotated_image = None
        
        # Enhanced hover scaling
        self.target_hover_scale = 1.15 if self.is_hovering else 1.0
        scale_speed = 8.0 * dt
        if abs(self.hover_scale - self.target_hover_scale) > 0.01:
            if self.hover_scale < self.target_hover_scale:
                self.hover_scale = min(self.target_hover_scale, self.hover_scale + scale_speed)
            else:
                self.hover_scale = max(self.target_hover_scale, self.hover_scale - scale_speed)
        
        # Update animations
        self.glow_animation += dt * 4
        self.pulse_animation += dt * 3
        
        return self.rect.bottom > -100
    
    def set_hover(self, hovering):
        """Set hover state for visual feedback - """
        if hovering != self.is_hovering and not self.popped:
            self.is_hovering = hovering
            self.glow_animation = 0
    
    def pop(self):
        """Pop the balloon"""
        if not self.popped:
            self.popped = True
            return True
        return False
    
    def check_collision(self, x, y, radius=None):
        """Check if point is within balloon collision area - OPTIMIZED"""
        if self.popped:
            return False
        
        if radius is None:
            radius = self.collision_radius
        
        # Quick distance check
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        distance_sq = dx * dx + dy * dy
        return distance_sq < radius * radius
    
    def draw(self, screen, time_elapsed):
        """Draw the balloon with enhanced effects"""
        if self.popped and self.pop_animation >= 1.0:
            return
        
        if self.popped:
            # Enhanced pop animation
            alpha = int(255 * (1 - self.pop_animation))
            if alpha > 0:
                # Scale down during pop
                pop_scale = 1.0 + self.pop_animation * 0.3
                temp_rect = self.rect.copy()
                temp_rect.width = int(temp_rect.width * pop_scale)
                temp_rect.height = int(temp_rect.height * pop_scale)
                temp_rect.center = self.rect.center
                
                temp_surface = self.current_image.copy()
                temp_surface.set_alpha(alpha)
                screen.blit(temp_surface, temp_rect)
        else:
            # Enhanced visual effects when not popped
            current_image = self.current_image
            draw_rect = self.rect.copy()
            
            # Apply hover scaling
            if abs(self.hover_scale - 1.0) > 0.01:
                old_center = draw_rect.center
                draw_rect.width = int(draw_rect.width * self.hover_scale)
                draw_rect.height = int(draw_rect.height * self.hover_scale)
                draw_rect.center = old_center
            
            # Enhanced glow effect when hovered
            if self.is_hovering:
                # Pulsing glow
                glow_intensity = 0.7 + 0.3 * math.sin(self.glow_animation)
                glow_radius = int(40 * glow_intensity)
                glow_alpha = int(60 * glow_intensity)
                
                # Multi-layer glow for depth
                for i, radius_mult in enumerate([1.2, 1.0, 0.8]):
                    current_radius = int(glow_radius * radius_mult)
                    current_alpha = int(glow_alpha * (0.3 + 0.7 * (1 - i * 0.3)))
                    if current_radius > 0 and current_alpha > 0:
                        glow_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surface, (255, 255, 255, current_alpha//3), 
                                         (current_radius, current_radius), current_radius)
                        screen.blit(glow_surface, 
                                   (draw_rect.centerx - current_radius, 
                                    draw_rect.centery - current_radius),
                                   special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Draw main balloon with rotation and scaling
            if self.rotated_image and abs(self.hover_scale - 1.0) > 0.01:
                # Both rotation and scaling
                scaled_image = pygame.transform.scale(self.rotated_image, 
                                                    (draw_rect.width, draw_rect.height))
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                screen.blit(scaled_image, scaled_rect)
            elif self.rotated_image:
                # Just rotation
                rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
                screen.blit(self.rotated_image, rotated_rect)
            elif abs(self.hover_scale - 1.0) > 0.01:
                # Just scaling
                scaled_image = pygame.transform.scale(current_image, 
                                                    (draw_rect.width, draw_rect.height))
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                screen.blit(scaled_image, scaled_rect)
            else:
                # No transformation
                screen.blit(current_image, self.rect)
            
            # Subtle shine effect
            if not self.is_hovering:  # Only when not hovered to avoid overlap
                shine_progress = (time_elapsed + self.shine_offset) * 0.5
                shine_alpha = int(30 * (0.5 + 0.5 * math.sin(shine_progress)))
                if shine_alpha > 0:
                    shine_size = self.rect.width // 4
                    shine_x = self.rect.centerx - shine_size // 2
                    shine_y = self.rect.centery - self.rect.height // 3
                    pygame.draw.ellipse(screen, (255, 255, 255, shine_alpha), 
                                      (shine_x, shine_y, shine_size, shine_size // 2))
        
        # Enhanced points preview when hovered
        if self.is_hovering and not self.popped:
            points_text = f"+{self.points}"
            font = pygame.font.Font(None, 26)
            
            # Pulsing points text
            pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_animation)
            points_surface = font.render(points_text, True, (255, 255, 100))
            
            if abs(pulse_scale - 1.0) > 0.01:
                scaled_width = int(points_surface.get_width() * pulse_scale)
                scaled_height = int(points_surface.get_height() * pulse_scale)
                points_surface = pygame.transform.scale(points_surface, (scaled_width, scaled_height))
            
            points_rect = points_surface.get_rect(center=(self.rect.centerx, self.rect.top - 25))
            
            # Enhanced background with shadow
            bg_rect = points_rect.inflate(12, 6)
            shadow_rect = bg_rect.copy()
            shadow_rect.move_ip(2, 2)
            
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect)
            pygame.draw.rect(screen, (255, 255, 100), bg_rect, 1)
            screen.blit(points_surface, points_rect)


class BalloonPopGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Balloon Pop - Enhanced Edition")
        
        # Pre-load and pre-scale all balloon images
        self.balloon_images = {}
        self.balloon_colors = ['orange', 'gray', 'cyan', 'pink', 'blue', 'red']
        
        # Create optimized balloon images
        self.create_optimized_balloon_images()
        
        # Game state
        self.balloons = []
        self.score = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.max_missed = 8  # Slightly more forgiving
        self.game_over = False
        self.level = 1
        self.spawn_timer = 0
        self.spawn_interval = 2.2  # Slightly slower initial spawn
        self.last_spawn_time = time.time()
        
        # Enhanced spawn control
        self.consecutive_spawns = 0
        self.max_consecutive = 3
        self.burst_cooldown = 0
        
        # Hand tracking
        self.last_pinch = False
        self.hand_trail = []
        self.max_trail_length = 6
        
        # Game progression
        self.balloons_for_next_level = 15
        
        # UI Elements
        self.create_game_buttons()
        
        # Enhanced effects system
        self.pop_effects = []
        self.max_pop_effects = 10
        
        # Performance optimization
        self.cached_fonts = {
            'small': pygame.font.Font(None, 24),
            'medium': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 48),
            'huge': pygame.font.Font(None, 64)
        }
        
        # Safe spawn zone (avoiding edges for better hand tracking)
        current_width, current_height = self.get_current_screen_size()
        self.spawn_margin = min(120, current_width * 0.15)  # 15% margin or 120px minimum
        
        # Initialize first spawn
        self.last_spawn_time = time.time()
    
    def create_optimized_balloon_images(self):
        """Load and pre-scale balloon images for better performance"""
        balloon_files = {
            'orange': 'assets/balloons/balon_adidas_orange.png',
            'gray': 'assets/balloons/balon_adidas_grey.png',
            'cyan': 'assets/balloons/balon_adidas_biru_muda.png',
            'pink': 'assets/balloons/balon_adidas_pink.png',
            'blue': 'assets/balloons/balon_adidas_biru.png',
            'red': 'assets/balloons/balon_adidas_merah.png'
        }

        # Enhanced scales with hover state
        scales = {
            'small': (65, 80),
            'medium': (85, 105),
            'large': (105, 130),
            'hover': (95, 118)  # Between medium and large
        }

        for color_name, file_path in balloon_files.items():
            self.balloon_images[color_name] = {}
            
            try:
                original_image = pygame.image.load(file_path).convert_alpha()
                
                for scale_name, (width, height) in scales.items():
                    scaled_image = pygame.transform.smoothscale(original_image, (width, height))
                    self.balloon_images[color_name][scale_name] = scaled_image
                    
                print(f"Enhanced {color_name} balloon loaded with {len(scales)} scales")
                
            except Exception as e:
                print(f"Could not load {file_path}: {e}, using enhanced fallback")
                self.create_enhanced_fallback_balloon_images(color_name, scales)
    
    def create_enhanced_fallback_balloon_images(self, color_name, scales):
        """Create enhanced fallback balloon images"""
        color_map = {
            'orange': (255, 165, 0),
            'gray': (128, 128, 128),
            'cyan': (0, 255, 255),
            'pink': (255, 192, 203),
            'blue': (0, 100, 255),
            'red': (255, 50, 50)
        }
        
        color = color_map.get(color_name, (255, 255, 255))
        self.balloon_images[color_name] = {}
        
        for scale_name, (width, height) in scales.items():
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Enhanced balloon shape with gradient effect
            balloon_rect = pygame.Rect(width//8, height//20, width*3//4, height*3//4)
            
            # Main balloon body
            pygame.draw.ellipse(surface, color, balloon_rect)
            
            # Multiple highlights for depth
            highlight1 = pygame.Rect(width//4, height//8, width//5, height//4)
            highlight_color1 = tuple(min(255, c + 80) for c in color)
            pygame.draw.ellipse(surface, highlight_color1, highlight1)
            
            highlight2 = pygame.Rect(width//3, height//6, width//8, height//6)
            highlight_color2 = tuple(min(255, c + 120) for c in color)
            pygame.draw.ellipse(surface, highlight_color2, highlight2)
            
            # Enhanced string with knot
            string_start = (balloon_rect.centerx, balloon_rect.bottom)
            string_end = (balloon_rect.centerx + 2, height - 5)
            pygame.draw.line(surface, (139, 69, 19), string_start, string_end, 3)
            
            # String knot
            knot_rect = pygame.Rect(balloon_rect.centerx - 2, balloon_rect.bottom - 3, 4, 6)
            pygame.draw.ellipse(surface, (100, 50, 0), knot_rect)
            
            self.balloon_images[color_name][scale_name] = surface
    
    def create_game_buttons(self):
        """Create enhanced game buttons"""
        current_width, current_height = self.get_current_screen_size()
        
        # Main restart button
        self.restart_button = AnimatedButton(
            current_width - 200, 20, 130, 50, "New Game", PURPLE, GREEN
        )
        
        # Game over overlay button
        self.game_over_restart_button = AnimatedButton(
            current_width//2 - 100, current_height//2 + 60, 200, 60, 
            "Play Again", (50, 50, 50), (100, 255, 100)
        )
    
    def recalculate_game_layout(self):
        """Recalculate enhanced game layout when screen size changes"""
        print("Recalculating Enhanced Balloon Pop layout...")
        self.create_game_buttons()
        
        current_width, current_height = self.get_current_screen_size()
        
        # Update spawn margin for new screen size
        self.spawn_margin = min(120, current_width * 0.15)
        
        # Update existing balloons' screen dimensions
        for balloon in self.balloons:
            balloon.screen_width = current_width
            balloon.screen_height = current_height
    
    def get_game_info(self):
        return {
            'name': 'Balloon Pop ',
            'description': 'Pop floating balloons with enhanced effects and smart spawn zones',
            'preview_color': (255, 120, 180)
        }
    
    def get_safe_spawn_x(self):
        """Get a safe X coordinate for spawning that works well with hand tracking"""
        current_width, current_height = self.get_current_screen_size()
        
        # Define safe zone (avoiding edges)
        safe_left = self.spawn_margin
        safe_right = current_width - self.spawn_margin
        safe_width = safe_right - safe_left
        
        if safe_width > 100:  # Ensure we have enough space
            return random.randint(int(safe_left), int(safe_right))
        else:
            # Fallback if screen is too narrow
            return random.randint(80, max(120, current_width - 80))
    
    def spawn_balloon(self):
        """Spawn a new balloon in safe zone - """
        current_width, current_height = self.get_current_screen_size()
        
        # Use safe spawn zone
        x = self.get_safe_spawn_x()
        y = current_height + random.randint(30, 80)  # Varied spawn height
        
        color_name = random.choice(self.balloon_colors)
        
        balloon = Balloon(x, y, self.balloon_images, color_name, current_width, current_height)
        self.balloons.append(balloon)
        
        print(f"Spawned {color_name} balloon at safe position: {x}")
    
    def spawn_balloon_burst(self):
        """Spawn multiple balloons in a controlled burst"""
        burst_size = random.randint(2, 4)
        current_width, current_height = self.get_current_screen_size()
        
        # Spread balloons across safe zone
        safe_left = self.spawn_margin
        safe_right = current_width - self.spawn_margin
        
        for i in range(burst_size):
            # Distribute evenly across safe zone
            x_ratio = (i + 0.5) / burst_size
            x = int(safe_left + (safe_right - safe_left) * x_ratio)
            x += random.randint(-30, 30)  # Add some randomness
            
            # Clamp to safe bounds
            x = max(safe_left, min(safe_right, x))
            
            y = current_height + random.randint(20, 100)
            color_name = random.choice(self.balloon_colors)
            
            balloon = Balloon(x, y, self.balloon_images, color_name, current_width, current_height)
            self.balloons.append(balloon)
        
        print(f"Spawned burst of {burst_size} balloons in safe zone")
    
    def handle_game_events(self, event):
        """Handle enhanced balloon pop game events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_button.is_clicked(event.pos, True):
                self.restart_game()
            elif self.game_over and self.game_over_restart_button.is_clicked(event.pos, True):
                self.restart_game()
            elif not self.game_over:  # Only allow balloon clicking when game is active
                # Check balloon clicks with improved collision
                for balloon in self.balloons[:]:  # Use slice to avoid modification during iteration
                    if balloon.check_collision(event.pos[0], event.pos[1]):
                        if balloon.pop():
                            self.score += balloon.points
                            self.balloons_popped += 1
                            self.create_enhanced_pop_effect(balloon)
                        break
    
    def create_enhanced_pop_effect(self, balloon):
        """Create enhanced celebration effects"""
        if len(self.pop_effects) < self.max_pop_effects:
            pop_effect = PopEffect(
                balloon.rect.centerx, 
                balloon.rect.centery,
                balloon.color_name,
                balloon.scale_type
            )
            self.pop_effects.append(pop_effect)
    
    def restart_game(self):
        """Restart the enhanced game"""
        self.balloons = []
        self.score = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.game_over = False
        self.level = 1
        self.spawn_interval = 2.2
        self.last_spawn_time = time.time()
        self.pop_effects = []
        self.hand_trail = []
        self.consecutive_spawns = 0
        self.burst_cooldown = 0
        print(" game restarted!")
    
    def update_game(self):
        """Update enhanced balloon pop game state"""
        # Always update UI buttons even during game over
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if hand tracking is not active
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
            
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        self.restart_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Update game over button if game is over
        if self.game_over:
            self.game_over_restart_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        if self.restart_button.is_hand_activated() or (self.game_over and self.game_over_restart_button.is_hand_activated()):
            self.restart_game()
        
        if self.game_over:
            return
            
        current_time = time.time()
        dt = 1/60  # Fixed timestep for consistency
        
        #  spawn logic with burst control
        if current_time - self.last_spawn_time > self.spawn_interval:
            if self.burst_cooldown <= 0:
                # Decide between single spawn or burst
                if (self.consecutive_spawns < self.max_consecutive and 
                    random.random() < 0.25 and len(self.balloons) < 8):  # Burst chance
                    self.spawn_balloon_burst()
                    self.consecutive_spawns += 1
                    self.burst_cooldown = 3.0  # Cooldown after burst
                else:
                    self.spawn_balloon()
                    self.consecutive_spawns = 0
            else:
                self.spawn_balloon()
                self.burst_cooldown -= (current_time - self.last_spawn_time)
            
            self.last_spawn_time = current_time
        
        # Update balloons with enhanced logic
        remaining_balloons = []
        for balloon in self.balloons:
            if balloon.update(dt, self.background_manager.time_elapsed):
                remaining_balloons.append(balloon)
            else:
                if not balloon.popped:
                    self.balloons_missed += 1
                    if self.balloons_missed >= self.max_missed:
                        self.game_over = True
        
        self.balloons = remaining_balloons
        
        # Update enhanced pop effects
        remaining_effects = []
        for effect in self.pop_effects:
            if effect.update(dt):
                remaining_effects.append(effect)
        self.pop_effects = remaining_effects
        
        # Enhanced hand tracking with mouse fallback
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if hand tracking is not active
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Enhanced hand trail with smoothing
        if hand_data.active and hand_data.hands_count > 0:
            # Smooth trail updates - only add if moved significantly
            if (not self.hand_trail or 
                abs(hand_data.x - self.hand_trail[-1][0]) > 5 or 
                abs(hand_data.y - self.hand_trail[-1][1]) > 5):
                self.hand_trail.append((hand_data.x, hand_data.y, current_time))
            
            # Trim trail
            if len(self.hand_trail) > self.max_trail_length:
                self.hand_trail.pop(0)
        
        # Enhanced balloon interaction - find closest balloon for hover
        closest_balloon = None
        min_distance = float('inf')
        hover_threshold = 50
        
        for balloon in self.balloons:
            if balloon.popped:
                continue
                
            distance = math.sqrt((hand_data.x - balloon.rect.centerx) ** 2 + 
                               (hand_data.y - balloon.rect.centery) ** 2)
            
            if distance < hover_threshold and distance < min_distance:
                min_distance = distance
                closest_balloon = balloon
        
        # Set hover states efficiently
        for balloon in self.balloons:
            balloon.set_hover(balloon == closest_balloon)
        
        # Enhanced pinch gesture handling
        if hand_data.pinching and not self.last_pinch and closest_balloon:
            if closest_balloon.pop():
                self.score += closest_balloon.points
                self.balloons_popped += 1
                self.create_enhanced_pop_effect(closest_balloon)
                
                # Bonus points for fast popping
                if len(self.balloons) > 5:
                    self.score += 10
        
        self.last_pinch = hand_data.pinching
        
        # Enhanced level progression
        if self.balloons_popped >= self.balloons_for_next_level:
            self.level += 1
            self.balloons_for_next_level += 12  # Slightly easier progression
            self.spawn_interval = max(0.8, self.spawn_interval - 0.15)  # Gradual speed increase
            
            # Level-up bonus
            level_bonus = self.level * 100
            self.score += level_bonus
            print(f"Level {self.level}! Bonus: {level_bonus}")
        
        # Update UI with enhanced interaction (moved from bottom)
        # This was moved up to ensure buttons work during game over
        
        if self.game_over:
            # Still update pop effects during game over for visual continuity
            dt = 1/60
            remaining_effects = []
            for effect in self.pop_effects:
                if effect.update(dt):
                    remaining_effects.append(effect)
            self.pop_effects = remaining_effects
            return
    
    def draw_game(self):
        """Draw enhanced balloon pop game"""
        current_width, current_height = self.get_current_screen_size()
        
        # Enhanced title with glow effect
        title_text = self.font_title.render("BALLOON POP", True, WHITE)
        title_rect = title_text.get_rect(center=(current_width//2, 60))
        
        # Add title glow
        glow_surface = self.font_title.render("BALLOON POP", True, (100, 200, 255))
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_rect = title_rect.copy()
            glow_rect.move_ip(offset)
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_text, title_rect)
        
        # Enhanced subtitle
        # subtitle_text = self.font_small.render("Enhanced effects • Smart spawn zones • Optimized performance", True, (255, 150, 200))
        # subtitle_rect = subtitle_text.get_rect(center=(current_width//2, 95))
        # self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw balloons
        for balloon in self.balloons:
            balloon.draw(self.screen, self.background_manager.time_elapsed)
        
        # Draw enhanced pop effects
        for effect in self.pop_effects:
            effect.draw(self.screen)
        
        # Enhanced hand trail with gradient
        if len(self.hand_trail) > 1:
            current_time = time.time()
            trail_points = []
            trail_colors = []
            
            for i, (x, y, timestamp) in enumerate(self.hand_trail[-6:]):
                age = current_time - timestamp
                if age < 0.5:  # Only show recent trail
                    alpha = max(50, int(255 * (1 - age / 0.5)))
                    trail_points.append((int(x), int(y)))
                    trail_colors.append((0, 255, 255, alpha))
            
            # Draw trail with varying thickness
            if len(trail_points) > 1:
                for i in range(len(trail_points) - 1):
                    thickness = max(1, 4 - i)
                    if i < len(trail_colors):
                        color = trail_colors[i][:3]  # Remove alpha for pygame.draw.line
                        pygame.draw.line(self.screen, color, trail_points[i], trail_points[i + 1], thickness)
        
        # Enhanced hand indicator
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            # Animated hand cursor
            pulse = math.sin(self.background_manager.time_elapsed * 4) * 0.2 + 1.0
            hand_color = GREEN if not hand_data.pinching else YELLOW
            radius = int(15 * pulse) if not hand_data.pinching else int(10 * pulse)
            
            # Draw hand indicator with pulse effect
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), radius)
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), radius, 3)
            
            # Draw crosshair for precision
            cross_size = 8
            pygame.draw.line(self.screen, hand_color, 
                           (hand_data.x - cross_size, hand_data.y), 
                           (hand_data.x + cross_size, hand_data.y), 2)
            pygame.draw.line(self.screen, hand_color, 
                           (hand_data.x, hand_data.y - cross_size), 
                           (hand_data.x, hand_data.y + cross_size), 2)
        
        # Enhanced game stats with better layout
        stats_x = 50
        stats_y = 140
        
        # Score with animation
        score_color = WHITE
        if hasattr(self, '_last_score') and self.score > self._last_score:
            score_color = YELLOW
        self._last_score = getattr(self, '_last_score', self.score)
        if abs(self.score - self._last_score) > 0:
            self._last_score += (self.score - self._last_score) * 0.1
        
        score_text = self.cached_fonts['large'].render(f"Score: {int(self._last_score)}", True, score_color)
        self.screen.blit(score_text, (stats_x, stats_y))
        
        level_text = self.cached_fonts['medium'].render(f"Level: {self.level}", True, CYAN)
        self.screen.blit(level_text, (stats_x, stats_y + 50))
        
        popped_text = self.cached_fonts['medium'].render(f"Popped: {self.balloons_popped}", True, GREEN)
        self.screen.blit(popped_text, (stats_x, stats_y + 80))
        
        # Enhanced missed counter with warning colors
        missed_ratio = self.balloons_missed / self.max_missed
        if missed_ratio >= 0.8:
            missed_color = RED
        elif missed_ratio >= 0.6:
            missed_color = YELLOW
        else:
            missed_color = WHITE
            
        missed_text = self.cached_fonts['medium'].render(f"Missed: {self.balloons_missed}/{self.max_missed}", True, missed_color)
        self.screen.blit(missed_text, (stats_x, stats_y + 110))
        
        # Progress to next level
        progress_text = self.cached_fonts['small'].render(f"Next Level: {self.balloons_popped}/{self.balloons_for_next_level}", True, LIGHT_GRAY)
        self.screen.blit(progress_text, (stats_x, stats_y + 140))
        
        # Enhanced spawn zone indicator (debug info)
        if hasattr(self, '_show_debug') and self._show_debug:
            safe_left = self.spawn_margin
            safe_right = current_width - self.spawn_margin
            pygame.draw.line(self.screen, (255, 255, 0, 100), (safe_left, 0), (safe_left, current_height), 2)
            pygame.draw.line(self.screen, (255, 255, 0, 100), (safe_right, 0), (safe_right, current_height), 2)
            
            debug_text = self.cached_fonts['small'].render(f"Safe spawn zone: {safe_left} - {safe_right}", True, YELLOW)
            self.screen.blit(debug_text, (stats_x, stats_y + 170))
        
        # Game status with enhanced feedback
        center_x = current_width // 2
        status_y = current_height - 140
        
        if self.game_over:
            # Enhanced game over overlay
            overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            # Game over panel
            panel_width = 400
            panel_height = 300
            panel_x = center_x - panel_width // 2
            panel_y = current_height // 2 - panel_height // 2
            
            # Panel background with border
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)
            pygame.draw.rect(self.screen, (100, 100, 150), panel_rect, 3)
            
            # Game over title
            game_over_text = self.cached_fonts['huge'].render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(center_x, panel_y + 60))
            
            # Add text shadow
            shadow_text = self.cached_fonts['huge'].render("GAME OVER", True, (80, 0, 0))
            shadow_rect = game_over_rect.copy()
            shadow_rect.move_ip(2, 2)
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(game_over_text, game_over_rect)
            
            # Stats
            final_score_text = self.cached_fonts['large'].render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(center_x, panel_y + 120))
            self.screen.blit(final_score_text, final_score_rect)
            
            level_reached_text = self.cached_fonts['medium'].render(f"Level Reached: {self.level}", True, CYAN)
            level_reached_rect = level_reached_text.get_rect(center=(center_x, panel_y + 155))
            self.screen.blit(level_reached_text, level_reached_rect)
            
            balloons_stats_text = self.cached_fonts['medium'].render(f"Balloons Popped: {self.balloons_popped}", True, GREEN)
            balloons_stats_rect = balloons_stats_text.get_rect(center=(center_x, panel_y + 185))
            self.screen.blit(balloons_stats_text, balloons_stats_rect)
            
            # Draw game over restart button
            self.game_over_restart_button.draw(self.screen, self.cached_fonts['medium'])
            
        else:
            # Enhanced status display
            balloon_count = len(self.balloons)
            balloon_color = RED if balloon_count > 15 else YELLOW if balloon_count > 10 else GREEN
            
            tracking_status = "Hand Active" if hand_data.active and hand_data.hands_count > 0 else "Mouse Mode"
            tracking_color = GREEN if hand_data.active and hand_data.hands_count > 0 else LIGHT_GRAY
            
            status = f"Balloons: {balloon_count} | Speed: {self.spawn_interval:.1f}s | {tracking_status}"
            status_text = self.cached_fonts['medium'].render(status, True, tracking_color)
            status_rect = status_text.get_rect(center=(center_x, status_y))
            self.screen.blit(status_text, status_rect)
            
            # Performance indicator
            fps_text = f"FPS: ~60 | Effects: {len(self.pop_effects)}"
            fps_color = GREEN if len(self.pop_effects) < 8 else YELLOW
            fps_surface = self.cached_fonts['small'].render(fps_text, True, fps_color)
            fps_rect = fps_surface.get_rect(center=(center_x, status_y + 25))
            self.screen.blit(fps_surface, fps_rect)
        
        # Draw restart button (always visible)
        self.restart_button.draw(self.screen, self.cached_fonts['small'])
        
        # Enhanced instructions
        instructions = [
            "PINCH to pop balloons | Smart spawn zones for better tracking",
            "Mouse click works too | R: Restart | ESC: Menu | Enhanced effects!"
        ]
        instruction_y = current_height - 50
        for i, instruction in enumerate(instructions):
            text = self.cached_fonts['small'].render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(center_x, instruction_y + i * 18))
            self.screen.blit(text, text_rect)