# games/balloon_pop.py - Fixed VERSION
"""
Balloon Pop Game using hand tracking
Pop balloons as they float up from the bottom
Fixed: ModernScoreWidget current_height issue and simplified start overlay
"""

import pygame
import random
import math
import time
from .base_game import BaseGame
from core import *

class ModernScoreWidget:
    """Modern score widget yang bisa di-toggle dengan animasi smooth"""
    def __init__(self, x, y, width=280, height=200):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_expanded = True
        self.target_expanded = True
        
        # Animation properties
        self.animation_progress = 1.0
        self.animation_speed = 4.0
        
        # Visual properties
        self.background_alpha = 180
        self.border_radius = 15
        self.collapsed_height = 50
        self.current_height = height  # FIX: Initialize current_height
        
        # Toggle button
        self.toggle_button = pygame.Rect(x + width - 40, y + 10, 30, 30)
        self.toggle_hover = False
        
        # Colors
        self.bg_color = (20, 25, 40)
        self.border_color = (70, 80, 120)
        self.accent_color = (100, 150, 255)
        self.text_color = (220, 225, 240)
        
        # Glow effect
        self.glow_animation = 0
        
    def update(self, dt, mouse_pos, mouse_clicked, hand_pos=None, hand_clicked=False):
        """Update widget dengan hand tracking support"""
        check_pos = hand_pos if hand_pos else mouse_pos
        self.toggle_hover = self.toggle_button.collidepoint(check_pos)
        
        clicked = hand_clicked if hand_pos else mouse_clicked
        if clicked and self.toggle_hover:
            self.target_expanded = not self.target_expanded
        
        target_progress = 1.0 if self.target_expanded else 0.0
        if abs(self.animation_progress - target_progress) > 0.01:
            if self.animation_progress < target_progress:
                self.animation_progress = min(1.0, self.animation_progress + self.animation_speed * dt)
            else:
                self.animation_progress = max(0.0, self.animation_progress - self.animation_speed * dt)
        
        self.glow_animation += dt * 3
        self.current_height = self.collapsed_height + (self.height - self.collapsed_height) * self.animation_progress
        
    def draw(self, screen, game_data, cached_fonts):
        """Draw modern score widget dengan smooth animations"""
        widget_surface = pygame.Surface((self.width, int(self.current_height)), pygame.SRCALPHA)
        
        bg_rect = pygame.Rect(0, 0, self.width, int(self.current_height))
        
        # Shadow layer
        shadow_rect = bg_rect.copy()
        shadow_rect.move_ip(3, 3)
        pygame.draw.rect(widget_surface, (0, 0, 0, 60), shadow_rect, border_radius=self.border_radius)
        
        # Main background
        pygame.draw.rect(widget_surface, (*self.bg_color, self.background_alpha), bg_rect, border_radius=self.border_radius)
        
        # Border dengan glow effect
        glow_intensity = 0.5 + 0.3 * math.sin(self.glow_animation)
        border_color = tuple(min(255, int(c * glow_intensity)) for c in self.border_color)
        pygame.draw.rect(widget_surface, border_color, bg_rect, 2, border_radius=self.border_radius)
        
        # Header bar
        header_rect = pygame.Rect(5, 5, self.width - 10, 40)
        header_color = tuple(min(255, c + 20) for c in self.bg_color)
        pygame.draw.rect(widget_surface, header_color, header_rect, border_radius=10)
        
        # Score title di header
        title_text = cached_fonts['medium'].render("SCORE", True, self.accent_color)
        title_rect = title_text.get_rect(left=15, centery=25)
        widget_surface.blit(title_text, title_rect)
        
        # Score value di header
        score_text = cached_fonts['medium'].render(str(game_data['score']), True, self.text_color)
        score_rect = score_text.get_rect(right=self.width - 50, centery=25)
        widget_surface.blit(score_text, score_rect)
        
        # Toggle button
        toggle_color = self.accent_color if self.toggle_hover else (80, 90, 120)
        toggle_rect = pygame.Rect(self.width - 40, 10, 30, 30)
        pygame.draw.rect(widget_surface, toggle_color, toggle_rect, border_radius=5)
        
        # Toggle icon (arrow)
        if self.target_expanded:
            arrow_points = [(self.width - 25, 20), (self.width - 30, 30), (self.width - 20, 30)]
        else:
            arrow_points = [(self.width - 25, 30), (self.width - 30, 20), (self.width - 20, 20)]
        
        pygame.draw.polygon(widget_surface, (255, 255, 255), arrow_points)
        
        # Expanded content
        if self.animation_progress > 0.1:
            content_alpha = min(255, int(255 * (self.animation_progress - 0.1) / 0.9))
            
            stats_y = 60
            stats_spacing = 25
            
            stats_data = [
                ("Level", str(game_data['level']), (100, 200, 255)),
                ("Popped", str(game_data['balloons_popped']), (100, 255, 100)),
                ("Missed", f"{game_data['balloons_missed']}/{game_data['max_missed']}", (255, 150, 150)),
                ("Progress", f"{game_data['balloons_popped']}/{game_data['balloons_for_next_level']}", (255, 255, 100))
            ]
            
            for i, (label, value, color) in enumerate(stats_data):
                if stats_y + i * stats_spacing < self.current_height - 10:
                    label_surface = cached_fonts['small'].render(label + ":", True, (*self.text_color, content_alpha))
                    label_rect = label_surface.get_rect(left=15, y=stats_y + i * stats_spacing)
                    
                    value_surface = cached_fonts['small'].render(value, True, (*color, content_alpha))
                    value_rect = value_surface.get_rect(right=self.width - 15, y=stats_y + i * stats_spacing)
                    
                    if label == "Progress" and self.animation_progress > 0.8:
                        progress_ratio = game_data['balloons_popped'] / max(1, game_data['balloons_for_next_level'])
                        bar_width = self.width - 30
                        bar_height = 4
                        bar_y = stats_y + i * stats_spacing + 18
                        
                        bar_bg_rect = pygame.Rect(15, bar_y, bar_width, bar_height)
                        pygame.draw.rect(widget_surface, (50, 50, 70), bar_bg_rect, border_radius=2)
                        
                        progress_width = int(bar_width * progress_ratio)
                        if progress_width > 0:
                            progress_rect = pygame.Rect(15, bar_y, progress_width, bar_height)
                            pygame.draw.rect(widget_surface, color, progress_rect, border_radius=2)
                    
                    if content_alpha > 0:
                        label_surface.set_alpha(content_alpha)
                        value_surface.set_alpha(content_alpha)
                        widget_surface.blit(label_surface, label_rect)
                        widget_surface.blit(value_surface, value_rect)
        
        screen.blit(widget_surface, (self.x, self.y))


class SimpleStartOverlay:
    """Simple start overlay tanpa animasi berat"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_showing = True
        
        # Buttons
        button_width = 200
        button_height = 60
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        self.start_button = AnimatedButton(
            center_x - button_width // 2, 
            center_y + 80, 
            button_width, button_height,
            "START GAME", 
            (30, 40, 60), 
            (100, 150, 255)
        )
    
    def update(self, dt, mouse_pos, mouse_clicked, hand_pos=None, hand_clicked=False):
        """Update overlay dengan hand tracking support"""
        if not self.is_showing:
            return False
        
        # Handle button interaction
        check_pos = hand_pos if hand_pos else mouse_pos
        clicked = hand_clicked if hand_pos else mouse_clicked
        
        self.start_button.update(mouse_pos, hand_pos, hand_clicked if hand_pos else False)
        
        # Check for start game
        if self.start_button.is_clicked(check_pos, clicked) or self.start_button.is_hand_activated():
            self.is_showing = False
            return False
        
        return True
    
    def draw(self, screen, cached_fonts):
        """Draw simple start overlay"""
        if not self.is_showing:
            return
        
        # Create transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((20, 25, 35))
        overlay.set_alpha(180)  # 0-255, dimana 180 = sekitar 70% transparan
        screen.blit(overlay, (0, 0))
        
        # Central content panel
        panel_width = 400
        panel_height = 300
        panel_x = self.screen_width // 2 - panel_width // 2
        panel_y = self.screen_height // 2 - panel_height // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (30, 35, 50), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 120, 180), panel_rect, 3, border_radius=10)
        
        # Title
        title_text = cached_fonts['huge'].render("BALLOON POP", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, panel_y + 80))
        screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "Use PINCH gesture or CLICK to pop balloons",
            "Pop balloons before they escape!"
        ]
        
        instruction_y = panel_y + 160
        for i, instruction in enumerate(instructions):
            instruction_surface = cached_fonts['small'].render(instruction, True, (200, 220, 240))
            instruction_rect = instruction_surface.get_rect(center=(self.screen_width // 2, instruction_y + i * 25))
            screen.blit(instruction_surface, instruction_rect)
        
        # Draw start button
        self.start_button.draw(screen, cached_fonts['medium'])


class PopEffect:
    """Separate class for enhanced pop effects"""
    def __init__(self, x, y, balloon_color, balloon_size):
        self.x = x
        self.y = y
        self.time = 0
        self.duration = 0.8
        self.balloon_color = balloon_color
        self.size_multiplier = {'small': 0.8, 'medium': 1.0, 'large': 1.2}.get(balloon_size, 1.0)
        
        # Create particle bursts
        self.particles = []
        particle_count = 8
        for i in range(particle_count):
            angle = (i / particle_count) * math.pi * 2
            speed = random.uniform(60, 120) * self.size_multiplier
            self.particles.append({
                'start_x': x,
                'start_y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - random.uniform(20, 40),
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
            particle['life'] = 1.0 - (progress * 1.5)
        
        # Update shockwave
        self.shockwave_radius = self.max_shockwave_radius * min(1.0, progress * 3)
        
        # Update stars
        for star in self.stars:
            star['rotation'] += dt * 360
        
        return True
    
    def draw(self, screen):
        """Draw enhanced pop effect"""
        progress = self.time / self.duration
        
        # Draw shockwave
        if progress < 0.3:
            shockwave_alpha = int(255 * (1 - progress / 0.3))
            if self.shockwave_radius > 0 and shockwave_alpha > 0:
                shockwave_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
                pygame.draw.circle(shockwave_surface, (255, 255, 255), 
                                 (100, 100), int(self.shockwave_radius), 3)
                shockwave_surface.set_alpha(shockwave_alpha//2)
                screen.blit(shockwave_surface, (self.x - 100, self.y - 100))
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                size = max(1, int(particle['size'] * particle['life']))
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
        points = []
        for i in range(4):
            angle = math.radians(rotation + i * 90)
            point_x = x + math.cos(angle) * size
            point_y = y + math.sin(angle) * size
            points.append((int(point_x), int(point_y)))
            
            inner_angle = math.radians(rotation + i * 90 + 45)
            inner_size = size * 0.4
            inner_x = x + math.cos(inner_angle) * inner_size
            inner_y = y + math.sin(inner_angle) * inner_size
            points.append((int(inner_x), int(inner_y)))
        
        if len(points) >= 6:
            pygame.draw.polygon(screen, color, points[:6])


class Balloon:
    """Individual balloon object"""
    def __init__(self, x, y, balloon_images_dict, color_name, screen_width, screen_height):
        self.images = balloon_images_dict[color_name]
        self.color_name = color_name
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Movement properties
        base_speed = random.uniform(1.2, 2.8)
        self.speed_y = base_speed
        self.speed_x = random.uniform(-0.3, 0.3)
        self.float_amplitude = random.uniform(8, 15)
        self.float_frequency = random.uniform(0.8, 1.2)
        self.initial_x = x
        
        # Visual properties
        self.scale_type = random.choice(['small', 'medium', 'large'])
        self.current_image = self.images[self.scale_type]
        self.rect = self.current_image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        
        # Animation properties
        self.rotation = 0
        self.rotation_speed = random.uniform(-1.5, 1.5)
        self.bob_offset = random.uniform(0, math.pi * 2)
        self.bounce_amplitude = random.uniform(0.5, 1.5)
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
        
        # Visual feedback
        self.pulse_animation = random.uniform(0, math.pi * 2)
        self.shine_offset = random.uniform(0, 1000)
        
        # Score value
        size_multiplier = {'small': 1.5, 'medium': 1.0, 'large': 0.7}[self.scale_type]
        speed_bonus = (self.speed_y - 1.2) / 1.6
        self.points = int(40 + speed_bonus * 60 * size_multiplier)
        
        # Collision
        self.collision_radius = {'small': 35, 'medium': 45, 'large': 55}[self.scale_type]
    
    def update(self, dt, time_elapsed):
        """Update balloon position and animations"""
        if self.popped:
            self.pop_animation += dt * 4
            return self.pop_animation < 1.0
        
        # Movement
        vertical_bounce = math.sin(time_elapsed * self.bounce_frequency + self.bob_offset) * self.bounce_amplitude
        self.rect.y -= self.speed_y + vertical_bounce * 0.1
        
        float_offset = math.sin(time_elapsed * self.float_frequency + self.bob_offset) * self.float_amplitude
        wind_effect = math.sin(time_elapsed * 0.3) * 5
        self.rect.centerx = self.initial_x + self.speed_x * time_elapsed + float_offset + wind_effect
        
        # Keep within bounds
        margin = 80
        if self.rect.centerx < margin:
            self.rect.centerx = margin
        elif self.rect.centerx > self.screen_width - margin:
            self.rect.centerx = self.screen_width - margin
        
        # Rotation
        new_rotation = self.rotation + self.rotation_speed * dt
        if abs(new_rotation - self.rotation_cache_angle) > 8:
            self.rotation = new_rotation
            if abs(self.rotation) > 2:
                self.rotated_image = pygame.transform.rotate(self.current_image, self.rotation)
                self.rotation_cache_angle = self.rotation
            else:
                self.rotated_image = None
        
        # Hover scaling
        self.target_hover_scale = 1.15 if self.is_hovering else 1.0
        scale_speed = 8.0 * dt
        if abs(self.hover_scale - self.target_hover_scale) > 0.01:
            if self.hover_scale < self.target_hover_scale:
                self.hover_scale = min(self.target_hover_scale, self.hover_scale + scale_speed)
            else:
                self.hover_scale = max(self.target_hover_scale, self.hover_scale - scale_speed)
        
        # Animations
        self.glow_animation += dt * 4
        self.pulse_animation += dt * 3
        
        return self.rect.bottom > -100
    
    def set_hover(self, hovering):
        """Set hover state for visual feedback"""
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
        """Check if point is within balloon collision area"""
        if self.popped:
            return False
        
        if radius is None:
            radius = self.collision_radius
        
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        distance_sq = dx * dx + dy * dy
        return distance_sq < radius * radius
    
    def draw(self, screen, time_elapsed):
        """Draw the balloon with enhanced effects"""
        if self.popped and self.pop_animation >= 1.0:
            return
        
        if self.popped:
            alpha = int(255 * (1 - self.pop_animation))
            if alpha > 0:
                pop_scale = 1.0 + self.pop_animation * 0.3
                temp_rect = self.rect.copy()
                temp_rect.width = int(temp_rect.width * pop_scale)
                temp_rect.height = int(temp_rect.height * pop_scale)
                temp_rect.center = self.rect.center
                
                temp_surface = self.current_image.copy()
                temp_surface.set_alpha(alpha)
                screen.blit(temp_surface, temp_rect)
        else:
            current_image = self.current_image
            draw_rect = self.rect.copy()
            
            # Apply hover scaling
            if abs(self.hover_scale - 1.0) > 0.01:
                old_center = draw_rect.center
                draw_rect.width = int(draw_rect.width * self.hover_scale)
                draw_rect.height = int(draw_rect.height * self.hover_scale)
                draw_rect.center = old_center
            
            # Glow effect when hovered
            if self.is_hovering:
                glow_intensity = 0.7 + 0.3 * math.sin(self.glow_animation)
                glow_radius = int(40 * glow_intensity)
                glow_alpha = int(60 * glow_intensity)
                
                for i, radius_mult in enumerate([1.2, 1.0, 0.8]):
                    current_radius = int(glow_radius * radius_mult)
                    current_alpha = int(glow_alpha * (0.3 + 0.7 * (1 - i * 0.3)))
                    if current_radius > 0 and current_alpha > 0:
                        glow_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                        glow_color = (255, 255, 255)
                        pygame.draw.circle(glow_surface, glow_color, 
                                         (current_radius, current_radius), current_radius)
                        glow_surface.set_alpha(current_alpha//3)
                        screen.blit(glow_surface, 
                                   (draw_rect.centerx - current_radius, 
                                    draw_rect.centery - current_radius))
            
            # Draw main balloon
            if self.rotated_image and abs(self.hover_scale - 1.0) > 0.01:
                scaled_image = pygame.transform.scale(self.rotated_image, 
                                                    (draw_rect.width, draw_rect.height))
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                screen.blit(scaled_image, scaled_rect)
            elif self.rotated_image:
                rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
                screen.blit(self.rotated_image, rotated_rect)
            elif abs(self.hover_scale - 1.0) > 0.01:
                scaled_image = pygame.transform.scale(current_image, 
                                                    (draw_rect.width, draw_rect.height))
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                screen.blit(scaled_image, scaled_rect)
            else:
                screen.blit(current_image, self.rect)
            
            # Shine effect
            if not self.is_hovering:
                shine_progress = (time_elapsed + self.shine_offset) * 0.5
                shine_alpha = int(30 * (0.5 + 0.5 * math.sin(shine_progress)))
                if shine_alpha > 0:
                    shine_size = self.rect.width // 4
                    shine_x = self.rect.centerx - shine_size // 2
                    shine_y = self.rect.centery - self.rect.height // 3
                    shine_surface = pygame.Surface((shine_size, shine_size // 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(shine_surface, (255, 255, 255), shine_surface.get_rect())
                    shine_surface.set_alpha(shine_alpha)
                    screen.blit(shine_surface, (shine_x, shine_y))
        
        # Points preview when hovered
        if self.is_hovering and not self.popped:
            points_text = f"+{self.points}"
            font = pygame.font.Font(None, 26)
            
            pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_animation)
            points_surface = font.render(points_text, True, (255, 255, 100))
            
            if abs(pulse_scale - 1.0) > 0.01:
                scaled_width = int(points_surface.get_width() * pulse_scale)
                scaled_height = int(points_surface.get_height() * pulse_scale)
                points_surface = pygame.transform.scale(points_surface, (scaled_width, scaled_height))
            
            points_rect = points_surface.get_rect(center=(self.rect.centerx, self.rect.top - 25))
            
            bg_rect = points_rect.inflate(12, 6)
            shadow_rect = bg_rect.copy()
            shadow_rect.move_ip(2, 2)
            
            pygame.draw.rect(screen, (0, 0, 0), shadow_rect)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 100), bg_rect, 1)
            screen.blit(points_surface, points_rect)


class BalloonPopGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Balloon Pop - Enhanced Edition")
        
        # Pre-load balloon images
        self.balloon_images = {}
        self.balloon_colors = ['orange', 'gray', 'cyan', 'pink', 'blue', 'red']
        self.create_optimized_balloon_images()
        
        # Game states
        self.game_state = "START"  # "START", "PLAYING", "GAME_OVER"
        
        # Game data
        self.balloons = []
        self.score = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.max_missed = 8
        self.game_over = False
        self.level = 1
        self.spawn_timer = 0
        self.spawn_interval = 2.2
        self.last_spawn_time = time.time()
        
        # Spawn control
        self.consecutive_spawns = 0
        self.max_consecutive = 3
        self.burst_cooldown = 0
        
        # Hand tracking
        self.last_pinch = False
        self.hand_trail = []
        self.max_trail_length = 6
        
        # Progression
        self.balloons_for_next_level = 15
        
        # Initialize UI
        current_width, current_height = self.get_current_screen_size()
        self.start_overlay = SimpleStartOverlay(current_width, current_height)  # FIX: Use SimpleStartOverlay
        self.init_score_widget()
        self.create_game_buttons()
        
        # Effects
        self.pop_effects = []
        self.max_pop_effects = 10
        
        # Fonts
        self.cached_fonts = {
            'small': pygame.font.Font(None, 24),
            'medium': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 48),
            'huge': pygame.font.Font(None, 64)
        }
        
        # Safe spawn zone
        self.spawn_margin = min(120, current_width * 0.15)
        
        print("Balloon Pop Game initialized with Simple Start Overlay!")
    
    def init_score_widget(self):
        """Initialize score widget"""
        current_width, current_height = self.get_current_screen_size()
        widget_width = 280
        self.score_widget = ModernScoreWidget(
            x=current_width//2 - widget_width//2,
            y=20,
            width=widget_width, 
            height=220
        )

    def update_score_widget(self):
        """Update score widget"""
        if self.game_state != "PLAYING":
            return
            
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        hand_data = self.hand_tracker.hand_data
        hand_pos = None
        hand_clicked = False
        
        if hand_data.active and hand_data.hands_count > 0:
            hand_pos = (hand_data.x, hand_data.y)
            hand_clicked = hand_data.pinching and not self.last_pinch
        
        game_data = {
            'score': self.score,
            'level': self.level,
            'balloons_popped': self.balloons_popped,
            'balloons_missed': self.balloons_missed,
            'max_missed': self.max_missed,
            'balloons_for_next_level': self.balloons_for_next_level
        }
        
        dt = 1/60
        self.score_widget.update(dt, mouse_pos, mouse_clicked, hand_pos, hand_clicked)

    def draw_score_widget(self):
        """Draw score widget"""
        if self.game_state != "PLAYING":
            return
            
        game_data = {
            'score': self.score,
            'level': self.level,
            'balloons_popped': self.balloons_popped,
            'balloons_missed': self.balloons_missed,
            'max_missed': self.max_missed,
            'balloons_for_next_level': self.balloons_for_next_level
        }
        
        self.score_widget.draw(self.screen, game_data, self.cached_fonts)
    
    def create_optimized_balloon_images(self):
        """Load and pre-scale balloon images"""
        balloon_files = {
            'orange': 'assets/balloons/balon_adidas_orange.png',
            'gray': 'assets/balloons/balon_adidas_grey.png',
            'cyan': 'assets/balloons/balon_adidas_biru_muda.png',
            'pink': 'assets/balloons/balon_adidas_pink.png',
            'blue': 'assets/balloons/balon_adidas_biru.png',
            'red': 'assets/balloons/balon_adidas_merah.png'
        }

        scales = {
            'small': (80, 95),
            'medium': (100, 120),
            'large': (120, 145),
            'hover': (110, 133)
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
                print(f"Could not load {file_path}: {e}, using fallback")
                self.create_enhanced_fallback_balloon_images(color_name, scales)
    
    def create_enhanced_fallback_balloon_images(self, color_name, scales):
        """Create fallback balloon images"""
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
            
            balloon_rect = pygame.Rect(width//8, height//20, width*3//4, height*3//4)
            
            pygame.draw.ellipse(surface, color, balloon_rect)
            
            highlight1 = pygame.Rect(width//4, height//8, width//5, height//4)
            highlight_color1 = tuple(min(255, c + 80) for c in color)
            pygame.draw.ellipse(surface, highlight_color1, highlight1)
            
            highlight2 = pygame.Rect(width//3, height//6, width//8, height//6)
            highlight_color2 = tuple(min(255, c + 120) for c in color)
            pygame.draw.ellipse(surface, highlight_color2, highlight2)
            
            string_start = (balloon_rect.centerx, balloon_rect.bottom)
            string_end = (balloon_rect.centerx + 2, height - 5)
            pygame.draw.line(surface, (139, 69, 19), string_start, string_end, 3)
            
            knot_rect = pygame.Rect(balloon_rect.centerx - 2, balloon_rect.bottom - 3, 4, 6)
            pygame.draw.ellipse(surface, (100, 50, 0), knot_rect)
            
            self.balloon_images[color_name][scale_name] = surface
    
    def create_game_buttons(self):
        """Create game buttons"""
        current_width, current_height = self.get_current_screen_size()
        
        self.restart_button = AnimatedButton(
            current_width - 200, 20, 130, 50, "New Game", PURPLE, GREEN
        )
        
        self.game_over_restart_button = AnimatedButton(
            current_width//2 - 100, current_height//2 + 60, 200, 60, 
            "Play Again", (50, 50, 50), (100, 255, 100)
        )
    
    def recalculate_game_layout(self):
        """Recalculate layout"""
        print("Recalculating Enhanced Balloon Pop layout...")
        current_width, current_height = self.get_current_screen_size()
        
        self.start_overlay = SimpleStartOverlay(current_width, current_height)  # FIX: Use SimpleStartOverlay
        self.create_game_buttons()
        self.spawn_margin = min(120, current_width * 0.15)
        
        widget_width = 280
        self.score_widget.x = current_width//2 - widget_width//2
        self.score_widget.y = 20
        
        self.score_widget.toggle_button = pygame.Rect(
            self.score_widget.x + self.score_widget.width - 40, 
            self.score_widget.y + 10, 30, 30
        )
        
        for balloon in self.balloons:
            balloon.screen_width = current_width
            balloon.screen_height = current_height
    
    def get_game_info(self):
        return {
            'name': 'Balloon Pop Enhanced',
            'description': 'Pop floating balloons with enhanced effects, smart spawn zones, and simple start overlay',
            'preview_color': (255, 120, 180)
        }
    
    def get_safe_spawn_x(self):
        """Get safe X coordinate for spawning"""
        current_width, current_height = self.get_current_screen_size()
        
        safe_left = self.spawn_margin
        safe_right = current_width - self.spawn_margin
        safe_width = safe_right - safe_left
        
        if safe_width > 100:
            return random.randint(int(safe_left), int(safe_right))
        else:
            return random.randint(80, max(120, current_width - 80))
    
    def spawn_balloon(self):
        """Spawn a new balloon in safe zone"""
        current_width, current_height = self.get_current_screen_size()
        
        x = self.get_safe_spawn_x()
        y = current_height + random.randint(30, 80)
        
        color_name = random.choice(self.balloon_colors)
        
        balloon = Balloon(x, y, self.balloon_images, color_name, current_width, current_height)
        self.balloons.append(balloon)
    
    def spawn_balloon_burst(self):
        """Spawn multiple balloons"""
        burst_size = random.randint(2, 4)
        current_width, current_height = self.get_current_screen_size()
        
        safe_left = self.spawn_margin
        safe_right = current_width - self.spawn_margin
        
        for i in range(burst_size):
            x_ratio = (i + 0.5) / burst_size
            x = int(safe_left + (safe_right - safe_left) * x_ratio)
            x += random.randint(-30, 30)
            
            x = max(safe_left, min(safe_right, x))
            
            y = current_height + random.randint(20, 100)
            color_name = random.choice(self.balloon_colors)
            
            balloon = Balloon(x, y, self.balloon_images, color_name, current_width, current_height)
            self.balloons.append(balloon)
    
    def start_new_game(self):
        """Start a fresh game session"""
        self.game_state = "PLAYING"
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
        print("New game started!")
    
    def handle_game_events(self, event):
        """Handle game events with start overlay support"""
        if self.game_state == "START":
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.restart_button.is_clicked(event.pos, True):
                self.restart_game()
            elif self.game_over and self.game_over_restart_button.is_clicked(event.pos, True):
                self.restart_game()
            elif not self.game_over and self.game_state == "PLAYING":
                for balloon in self.balloons[:]:
                    if balloon.check_collision(event.pos[0], event.pos[1]):
                        if balloon.pop():
                            self.score += balloon.points
                            self.balloons_popped += 1
                            self.create_enhanced_pop_effect(balloon)
                        break
    
    def create_enhanced_pop_effect(self, balloon):
        """Create pop effects"""
        if len(self.pop_effects) < self.max_pop_effects:
            pop_effect = PopEffect(
                balloon.rect.centerx, 
                balloon.rect.centery,
                balloon.color_name,
                balloon.scale_type
            )
            self.pop_effects.append(pop_effect)
    
    def restart_game(self):
        """Restart the game"""
        if self.game_state == "START":
            self.start_new_game()
        else:
            self.game_state = "START"
            current_width, current_height = self.get_current_screen_size()
            self.start_overlay = SimpleStartOverlay(current_width, current_height)
            self.balloons = []
            self.pop_effects = []
            self.hand_trail = []
            print("Game restarted - returning to simple start overlay!")
    
    def update_game(self):
        """Update game state with start overlay"""
        dt = 1/60
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        hand_data = self.hand_tracker.hand_data
        hand_pos = None
        hand_clicked = False
        
        if hand_data.active and hand_data.hands_count > 0:
            hand_pos = (hand_data.x, hand_data.y)
            hand_clicked = hand_data.pinching and not self.last_pinch
        
        # Handle different game states
        if self.game_state == "START":
            overlay_active = self.start_overlay.update(dt, mouse_pos, mouse_clicked, hand_pos, hand_clicked)
            
            if not overlay_active:
                self.start_new_game()
            
            return
        
        # Update UI buttons
        self.restart_button.update(mouse_pos, hand_pos, hand_data.pinching if hand_pos else False)
        
        if self.game_over:
            self.game_over_restart_button.update(mouse_pos, hand_pos, hand_data.pinching if hand_pos else False)
        
        if self.restart_button.is_hand_activated():
            self.restart_game()
        elif self.game_over and self.game_over_restart_button.is_hand_activated():
            self.restart_game()

        self.update_score_widget()
        
        if self.game_over:
            remaining_effects = []
            for effect in self.pop_effects:
                if effect.update(dt):
                    remaining_effects.append(effect)
            self.pop_effects = remaining_effects
            return
            
        current_time = time.time()
        
        # Spawn logic
        if current_time - self.last_spawn_time > self.spawn_interval:
            if self.burst_cooldown <= 0:
                if (self.consecutive_spawns < self.max_consecutive and 
                    random.random() < 0.25 and len(self.balloons) < 8):
                    self.spawn_balloon_burst()
                    self.consecutive_spawns += 1
                    self.burst_cooldown = 3.0
                else:
                    self.spawn_balloon()
                    self.consecutive_spawns = 0
            else:
                self.spawn_balloon()
                self.burst_cooldown -= (current_time - self.last_spawn_time)
            
            self.last_spawn_time = current_time
        
        # Update balloons
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
        
        # Update pop effects
        remaining_effects = []
        for effect in self.pop_effects:
            if effect.update(dt):
                remaining_effects.append(effect)
        self.pop_effects = remaining_effects
        
        # Hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Hand trail
        if hand_data.active and hand_data.hands_count > 0:
            if (not self.hand_trail or 
                abs(hand_data.x - self.hand_trail[-1][0]) > 5 or 
                abs(hand_data.y - self.hand_trail[-1][1]) > 5):
                self.hand_trail.append((hand_data.x, hand_data.y, current_time))
            
            if len(self.hand_trail) > self.max_trail_length:
                self.hand_trail.pop(0)
        
        # Balloon interaction
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
        
        for balloon in self.balloons:
            balloon.set_hover(balloon == closest_balloon)
        
        # Pinch gesture handling
        if hand_data.pinching and not self.last_pinch and closest_balloon:
            if closest_balloon.pop():
                self.score += closest_balloon.points
                self.balloons_popped += 1
                self.create_enhanced_pop_effect(closest_balloon)
                
                if len(self.balloons) > 5:
                    self.score += 10
        
        self.last_pinch = hand_data.pinching
        
        # Level progression
        if self.balloons_popped >= self.balloons_for_next_level:
            self.level += 1
            self.balloons_for_next_level += 12
            self.spawn_interval = max(0.8, self.spawn_interval - 0.15)
            
            level_bonus = self.level * 100
            self.score += level_bonus
            print(f"Level {self.level}! Bonus: {level_bonus}")
    
    def draw_hand_indicator(self):
        """Draw hand tracking indicator - separate method for reuse"""
        hand_data = self.hand_tracker.hand_data
        
        # Show mouse position when hand tracking is not active
        if not hand_data.active or hand_data.hands_count == 0:
            mouse_pos = pygame.mouse.get_pos()
            hand_data.x, hand_data.y = mouse_pos
        
        # Always draw hand/mouse indicator
        if hasattr(hand_data, 'x') and hasattr(hand_data, 'y'):
            pulse = math.sin(self.background_manager.time_elapsed * 4) * 0.2 + 1.0
            
            # Different colors for hand vs mouse tracking
            if hand_data.active and hand_data.hands_count > 0:
                hand_color = GREEN if not hand_data.pinching else YELLOW
                indicator_text = "HAND"
            else:
                hand_color = CYAN
                indicator_text = "MOUSE"
            
            radius = int(15 * pulse) if not (hand_data.active and hand_data.pinching) else int(10 * pulse)
            
            # Main indicator circle
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), radius)
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), radius, 3)
            
            # Cross hair
            cross_size = 8
            pygame.draw.line(self.screen, hand_color, 
                           (hand_data.x - cross_size, hand_data.y), 
                           (hand_data.x + cross_size, hand_data.y), 2)
            pygame.draw.line(self.screen, hand_color, 
                           (hand_data.x, hand_data.y - cross_size), 
                           (hand_data.x, hand_data.y + cross_size), 2)
            
            # Status text
            if hasattr(self, 'cached_fonts'):
                status_text = self.cached_fonts['small'].render(indicator_text, True, hand_color)
                text_rect = status_text.get_rect(center=(hand_data.x, hand_data.y - 35))
                
                # Background for text
                bg_rect = text_rect.inflate(8, 4)
                pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
                pygame.draw.rect(self.screen, hand_color, bg_rect, 1)
                
                self.screen.blit(status_text, text_rect)
                
    def draw_game(self):
        """Draw game with start overlay support"""
        current_width, current_height = self.get_current_screen_size()
        
        if self.game_state == "START":
            self.start_overlay.draw(self.screen, self.cached_fonts)
            # Draw hand indicator on start overlay too
            self.draw_hand_indicator()
            return
        
        # Draw game content
        for balloon in self.balloons:
            balloon.draw(self.screen, self.background_manager.time_elapsed)
        
        for effect in self.pop_effects:
            effect.draw(self.screen)
        
        # Hand trail
        if len(self.hand_trail) > 1:
            current_time = time.time()
            trail_points = []
            
            for i, (x, y, timestamp) in enumerate(self.hand_trail[-6:]):
                age = current_time - timestamp
                if age < 0.5:
                    trail_points.append((int(x), int(y)))
            
            if len(trail_points) > 1:
                for i in range(len(trail_points) - 1):
                    thickness = max(1, 4 - i)
                    color = (0, 255, 255)
                    pygame.draw.line(self.screen, color, trail_points[i], trail_points[i + 1], thickness)
        
        # Hand indicator (using separate method)
        self.draw_hand_indicator()
        
        self.draw_score_widget()
        
        center_x = current_width // 2
        
        if self.game_over:
            overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            panel_width = 400
            panel_height = 300
            panel_x = center_x - panel_width // 2
            panel_y = current_height // 2 - panel_height // 2
            
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)
            pygame.draw.rect(self.screen, (100, 100, 150), panel_rect, 3)
            
            game_over_text = self.cached_fonts['huge'].render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(center_x, panel_y + 60))
            
            shadow_text = self.cached_fonts['huge'].render("GAME OVER", True, (80, 0, 0))
            shadow_rect = game_over_rect.copy()
            shadow_rect.move_ip(2, 2)
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(game_over_text, game_over_rect)
            
            final_score_text = self.cached_fonts['large'].render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(center_x, panel_y + 120))
            self.screen.blit(final_score_text, final_score_rect)
            
            level_reached_text = self.cached_fonts['medium'].render(f"Level Reached: {self.level}", True, CYAN)
            level_reached_rect = level_reached_text.get_rect(center=(center_x, panel_y + 155))
            self.screen.blit(level_reached_text, level_reached_rect)
            
            balloons_stats_text = self.cached_fonts['medium'].render(f"Balloons Popped: {self.balloons_popped}", True, GREEN)
            balloons_stats_rect = balloons_stats_text.get_rect(center=(center_x, panel_y + 185))
            self.screen.blit(balloons_stats_text, balloons_stats_rect)
            
            self.game_over_restart_button.draw(self.screen, self.cached_fonts['medium'])
        
        self.restart_button.draw(self.screen, self.cached_fonts['small'])
        
        instructions = [
            "PINCH or CLICK to pop balloons",
            "Developed and Maintained by GVI PT. Maxima Cipta Miliardatha development team"
        ]
        instruction_y = current_height - 50
        for i, instruction in enumerate(instructions):
            text = self.cached_fonts['small'].render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(center_x, instruction_y + i * 18))
            self.screen.blit(text, text_rect)