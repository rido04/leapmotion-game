# games/fruit_ninja_game.py
"""
Fruit Ninja style game with hand tracking - Optimized for better performance
Reduced to 3 fruit types for improved performance
"""

import pygame
import math
import random
import os
from .base_game import BaseGame
from core import *


class SimpleParticle:
    """Simplified particle system for better performance"""
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 1.0
        self.size = random.randint(3, 6)
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.3  # Gravity
        self.velocity_x *= 0.95  # Air resistance
        self.life -= 0.03  # Fade speed
        
    def draw(self, screen):
        if self.life > 0:
            alpha_factor = self.life
            size = max(1, int(self.size * alpha_factor))
            color = (
                min(255, int(self.color[0] * alpha_factor)),
                min(255, int(self.color[1] * alpha_factor)),
                min(255, int(self.color[2] * alpha_factor))
            )
            if size > 0:
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)


class SimpleSplash:
    """Simplified splash effect"""
    def __init__(self, x, y, color):
        self.particles = []
        self.life = 1.0
        
        # Create fewer particles for better performance
        for i in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(1, 3)
            
            particle = SimpleParticle(x, y, color, vel_x, vel_y)
            self.particles.append(particle)
    
    def update(self):
        self.life -= 0.03
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
    
    def is_finished(self):
        return len(self.particles) == 0


class SliceEffect:
    """Simple slice line effect"""
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.life = 0.2  # Shorter duration
        self.max_life = 0.2
        
    def update(self, dt):
        self.life -= dt
        
    def draw(self, screen):
        if self.life > 0:
            alpha_factor = self.life / self.max_life
            thickness = max(1, int(6 * alpha_factor))
            color_intensity = int(255 * alpha_factor)
            slice_color = (color_intensity, color_intensity, color_intensity)
            pygame.draw.line(screen, slice_color, (self.x1, self.y1), (self.x2, self.y2), thickness)


class SwipeTrail:
    def __init__(self):
        self.points = []
        self.max_points = 8  # Reduced for better performance
        
    def add_point(self, x, y):
        self.points.append((x, y))
        if len(self.points) > self.max_points:
            self.points.pop(0)
    
    def clear(self):
        self.points = []
    
    def draw(self, screen):
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                alpha = (i / len(self.points))
                thickness = max(1, int(alpha * 8))
                pygame.draw.line(screen, WHITE, self.points[i], self.points[i + 1], thickness)


class FruitObject:
    _loaded_images = {}
    _prerendered_rotations = {}
    _images_loaded = False
    
    @classmethod
    def load_fruit_images(cls):
        if cls._images_loaded:
            return
            
        # REDUCED TO 3 FRUIT TYPES FOR BETTER PERFORMANCE
        fruit_files = {
            'apple': 'apple.png',
            'orange': 'orange.png', 
            'banana': 'banana.png'
        }
        
        assets_path = os.path.join('assets', 'fruits')
        
        for fruit_type, filename in fruit_files.items():
            try:
                image_path = os.path.join(assets_path, filename)
                original_image = pygame.image.load(image_path).convert_alpha()
                scaled_image = pygame.transform.scale(original_image, (200, 200))
                cls._loaded_images[fruit_type] = scaled_image
                
                # Pre-render rotations every 15 degrees (24 total rotations)
                cls._prerendered_rotations[fruit_type] = {}
                for angle in range(0, 360, 15):
                    rotated = pygame.transform.rotate(scaled_image, angle)
                    cls._prerendered_rotations[fruit_type][angle] = rotated
                
            except pygame.error:
                fallback_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                # UPDATED FALLBACK COLORS FOR 3 FRUITS
                fallback_colors = {
                    'apple': (255, 0, 0),
                    'orange': (255, 165, 0),
                    'banana': (255, 255, 0)
                }
                color = fallback_colors.get(fruit_type, (255, 255, 255))
                pygame.draw.circle(fallback_surface, color, (60, 60), 55)
                pygame.draw.circle(fallback_surface, (255, 255, 255), (60, 60), 55, 4)
                cls._loaded_images[fruit_type] = fallback_surface
                
                # Pre-render rotations for fallback too
                cls._prerendered_rotations[fruit_type] = {}
                for angle in range(0, 360, 15):
                    rotated = pygame.transform.rotate(fallback_surface, angle)
                    cls._prerendered_rotations[fruit_type][angle] = rotated
        
        # Bomb image with pre-rendered rotations
        bomb_surface = pygame.Surface((110, 110), pygame.SRCALPHA)
        pygame.draw.circle(bomb_surface, (64, 64, 64), (55, 55), 45)
        pygame.draw.circle(bomb_surface, (255, 0, 0), (55, 55), 45, 4)
        pygame.draw.line(bomb_surface, (255, 255, 0), (55, 55), (75, 30), 6)
        pygame.draw.circle(bomb_surface, (255, 255, 0), (75, 30), 6)
        cls._loaded_images['bomb'] = bomb_surface
        
        # Pre-render bomb rotations
        cls._prerendered_rotations['bomb'] = {}
        for angle in range(0, 360, 15):
            rotated = pygame.transform.rotate(bomb_surface, angle)
            cls._prerendered_rotations['bomb'][angle] = rotated
        
        cls._images_loaded = True

    def __init__(self, x, y, fruit_type, screen_width, screen_height):
        FruitObject.load_fruit_images()
        
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.fruit_type = fruit_type
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Physics
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-20, -15)
        self.gravity = 0.45
        self.rotation = 0
        self.rotation_speed = random.uniform(-8, 8)
        
        # Visual
        self.sliced = False
        self.slice_angle = 0
        self.size = 60
        self.visual_size = 60
        
        # Simplified slice effects
        self.juice_splash = None
        self.slice_effects = []
        self.slice_timer = 0
        
        self.image = FruitObject._loaded_images.get(fruit_type)
        # Initialize with 0-degree rotation
        self.current_rotated_image = FruitObject._prerendered_rotations.get(fruit_type, {}).get(0, self.image)
        
        # UPDATED FRUIT COLORS FOR 3 FRUITS
        self.fruit_colors = {
            'apple': (255, 50, 50),
            'orange': (255, 140, 0),
            'banana': (255, 255, 50),
            'bomb': (100, 100, 100)
        }
        
        # UPDATED SCORING FOR 3 FRUITS
        self.points = {
            'apple': 15,     # Increased points since fewer fruits
            'orange': 20,    # Increased points since fewer fruits
            'banana': 25,    # Increased points since fewer fruits
            'bomb': 25
        }

    def update(self, dt=1/60):
        if not self.sliced:
            self.x += self.velocity_x
            self.y += self.velocity_y
            self.velocity_y += self.gravity
            self.rotation += self.rotation_speed
            
            # Use pre-rendered rotation instead of real-time rotation
            if self.image:
                # Normalize rotation to 0-359 range
                normalized_rotation = self.rotation % 360
                # Find closest pre-rendered angle (every 15 degrees)
                closest_angle = round(normalized_rotation / 15) * 15
                if closest_angle >= 360:
                    closest_angle = 0
                
                # Get pre-rendered image
                prerendered_rotations = FruitObject._prerendered_rotations.get(self.fruit_type, {})
                self.current_rotated_image = prerendered_rotations.get(closest_angle, self.image)
        else:
            self.slice_timer += dt
        
        # Update simplified effects
        if self.juice_splash:
            self.juice_splash.update()
            if self.juice_splash.is_finished():
                self.juice_splash = None
        
        for effect in self.slice_effects[:]:
            effect.update(dt)
            if effect.life <= 0:
                self.slice_effects.remove(effect)

    def is_off_screen(self):
        return (self.y > self.screen_height + 150 or 
                self.x < -150 or self.x > self.screen_width + 150)
    
    def check_swipe_collision(self, trail_points):
        if self.sliced or len(trail_points) < 2:
            return False
            
        for i in range(len(trail_points) - 1):
            x1, y1 = trail_points[i]
            x2, y2 = trail_points[i + 1]
            
            if self.line_circle_collision(x1, y1, x2, y2, self.x, self.y, self.size//2):
                self.slice(x1, y1, x2, y2)
                return True
        
        return False
    
    def line_circle_collision(self, x1, y1, x2, y2, cx, cy, radius):
        A = x2 - x1
        B = y2 - y1
        C = x1 - cx
        D = y1 - cy
        
        dot = A * A + B * B
        if dot == 0:
            return False
            
        param = -(A * C + B * D) / dot
        
        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * A
            yy = y1 + param * B
        
        dx = cx - xx
        dy = cy - yy
        return dx * dx + dy * dy <= radius * radius
    
    def slice(self, x1, y1, x2, y2):
        if self.sliced:
            return
            
        self.sliced = True
        self.slice_angle = math.atan2(y2 - y1, x2 - x1)
        
        # Create simplified splash effect
        color = self.fruit_colors[self.fruit_type]
        self.juice_splash = SimpleSplash(self.x, self.y, color)
        
        # Create slice line effect
        slice_effect = SliceEffect(x1, y1, x2, y2)
        self.slice_effects.append(slice_effect)
    
    def get_score(self):
        if self.fruit_type == 'bomb':
            return 25
        return self.points.get(self.fruit_type, 0)
    
    def draw(self, screen):
        # Draw effects first
        if self.juice_splash:
            self.juice_splash.draw(screen)
        
        for effect in self.slice_effects:
            effect.draw(screen)
        
        if not self.sliced:
            # Draw whole fruit
            if self.current_rotated_image:
                image_rect = self.current_rotated_image.get_rect()
                image_rect.center = (int(self.x), int(self.y))
                screen.blit(self.current_rotated_image, image_rect)
            else:
                color = self.fruit_colors.get(self.fruit_type, (255, 255, 255))
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.visual_size)
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.visual_size, 3)
        else:
            # Draw simplified sliced fruit
            if self.slice_timer < 0.5:  # Only show for 0.5 seconds
                if self.image:
                    progress = self.slice_timer / 0.5
                    half_size = max(20, int(60 - progress * 20))
                    
                    if half_size > 15:
                        half_image = pygame.transform.scale(self.image, (half_size, half_size))
                        
                        offset = progress * 20
                        offset_x = math.cos(self.slice_angle) * offset
                        offset_y = math.sin(self.slice_angle) * offset
                        
                        # Draw two halves
                        half_rect1 = half_image.get_rect()
                        half_rect1.center = (int(self.x - offset_x), int(self.y - offset_y))
                        screen.blit(half_image, half_rect1)
                        
                        half_rect2 = half_image.get_rect() 
                        half_rect2.center = (int(self.x + offset_x), int(self.y + offset_y))
                        screen.blit(half_image, half_rect2)


class ScoreToggle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 30
        self.expanded = True
        self.hover = False
        self.click_timer = 0
        self.hand_click_timer = 0  # Tambah timer khusus untuk hand gesture
        self.animation_progress = 1.0 if self.expanded else 0.0
        self.target_progress = 1.0 if self.expanded else 0.0
        self.animation_speed = 4.0  # Speed of animation
        
    def update(self, mouse_pos, hand_pos, is_clicking):
        # Check hover
        check_pos = hand_pos if hand_pos else mouse_pos
        if check_pos:
            self.hover = (self.x <= check_pos[0] <= self.x + self.width and 
                         self.y <= check_pos[1] <= self.y + self.height)
        
        # Update click timers
        if self.click_timer > 0:
            self.click_timer -= 1/60
        if self.hand_click_timer > 0:
            self.hand_click_timer -= 1/60
        
        # Handle hand gesture clicking
        if self.hover and is_clicking and self.hand_click_timer <= 0:
            self.expanded = not self.expanded
            self.target_progress = 1.0 if self.expanded else 0.0
            self.hand_click_timer = 0.5
        
        # Smooth animation
        dt = 1/60
        if self.animation_progress < self.target_progress:
            self.animation_progress = min(self.target_progress, 
                                        self.animation_progress + self.animation_speed * dt)
        elif self.animation_progress > self.target_progress:
            self.animation_progress = max(self.target_progress, 
                                        self.animation_progress - self.animation_speed * dt)
    
    def is_clicked(self, pos, mouse_click=False):
        if mouse_click:
            if (self.x <= pos[0] <= self.x + self.width and 
                self.y <= pos[1] <= self.y + self.height):
                if self.click_timer <= 0:
                    self.expanded = not self.expanded
                    self.target_progress = 1.0 if self.expanded else 0.0
                    self.click_timer = 0.3
                    return True
        return False
    
    def is_animating(self):
        return self.animation_progress != self.target_progress
    
    def is_hand_activated(self):
        return False  # Handled in main update loop
    
    def draw(self, screen, font):
        # Background dengan hover effect
        base_color = (60, 60, 60)
        hover_color = (80, 80, 80)
        
        if self.hover:
            color = hover_color
        else:
            color = base_color
            
        # Rounded rectangle background
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height), 2, border_radius=8)
        
        # Text tanpa emoticon
        text = "Hide Score" if self.expanded else "Show Score"
        text_surface = font.render(text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text_surface, text_rect)


class FruitNinjaGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Shoe Slash Challenge")
        
        # Hand tracking for swipe
        self.swipe_trail = SwipeTrail()
        self.hand_history = []
        self.max_hand_history = 6  # Reduced for better performance
        self.swipe_threshold = 12
        
        # Screen shake effect
        self.screen_shake = 0
        self.shake_duration = 0
        
        # Game state
        self.reset_game()
        
        # Spawn timing
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        
        # Visual effects
        self.combo_timer = 0
        self.combo_count = 0
        self.last_combo_time = 0
        
        # Score toggle
        self.score_toggle = None
        
        # Buttons
        self.create_game_buttons()
    
    def create_game_buttons(self):
        current_width, current_height = self.get_current_screen_size()
        
        # Score toggle di tengah atas
        self.score_toggle = ScoreToggle(current_width//2 - 60, 20)
        
        # Start button
        self.start_button = AnimatedButton(
            current_width//2 - 75, current_height//2 + 50, 150, 60, "Start Game", (0, 255, 0), (100, 255, 100)
        )
        
        self.reset_button_normal = AnimatedButton(
            current_width - 190, 20, 120, 50, "Reset", (255, 165, 0), (255, 200, 100)
        )
        self.reset_button_game_over = AnimatedButton(
            current_width//2 - 75, current_height//2 + 80, 150, 60, "Play Again", (255, 165, 0), (255, 200, 100)
        )
    
    def recalculate_game_layout(self):
        self.create_game_buttons()
        current_width, current_height = self.get_current_screen_size()
        for fruit in self.fruits:
            fruit.screen_width = current_width
            fruit.screen_height = current_height
    
    def get_game_info(self):
        return {
            'name': 'Shoe Slash',
            'description': 'Slice fruits with hand gestures',
            'preview_color': (255, 165, 0)
        }
    
    def reset_game(self):
        self.score = 0
        self.lives = 5
        self.game_time = 60.0
        self.game_over = False
        self.game_started = False
        self.fruits = []
        self.particles = []
        self.combo_count = 0
        self.combo_timer = 0
        self.spawn_timer = 0
        
        self.screen_shake = 0
        self.shake_duration = 0
        
        # Frenzy mode
        self.frenzy_mode = False
        self.frenzy_timer = 0
        self.frenzy_cooldown = 0
        self.frenzy_threshold = 500
        self.next_frenzy_score = self.frenzy_threshold
        self.frenzy_count = 0
        
        # Multi-spawn system
        self.multi_spawn_chance = 0.3
        
        if hasattr(self, 'swipe_trail'):
            self.swipe_trail.clear()
        if hasattr(self, 'hand_history'):
            self.hand_history = []
    
    def spawn_fruit(self):
        current_width, current_height = self.get_current_screen_size()
        
        if self.frenzy_mode:
            spawn_count = random.randint(2, 4)
        elif random.random() < self.multi_spawn_chance:
            spawn_count = random.randint(2, 3)
        else:
            spawn_count = 1
        
        for _ in range(spawn_count):
            spawn_x = random.randint(120, current_width - 120)
            spawn_y = current_height + 20
            
            if self.frenzy_mode:
                # UPDATED TO USE ONLY 3 FRUIT TYPES
                fruit_types = ['apple', 'orange', 'banana']
                if random.random() < 0.1:
                    fruit_type = 'bomb'
                else:
                    fruit_type = random.choice(fruit_types)
            else:
                # UPDATED FRUIT WEIGHTS FOR 3 FRUITS
                fruit_weights = [
                    ('apple', 80),   # Increased weight for better distribution
                    ('orange', 80),  # Increased weight for better distribution
                    ('banana', 80),  # Increased weight for better distribution
                    ('bomb', 80)     # Increased weight to maintain challenge
                ]
                
                total_weight = sum(weight for _, weight in fruit_weights)
                random_num = random.randint(1, total_weight)
                
                cumulative_weight = 0
                fruit_type = 'apple'
                
                for fruit, weight in fruit_weights:
                    cumulative_weight += weight
                    if random_num <= cumulative_weight:
                        fruit_type = fruit
                        break
            
            fruit = FruitObject(spawn_x, spawn_y, fruit_type, current_width, current_height)
            extra_boost = random.uniform(3, 6) if not self.frenzy_mode else random.uniform(4, 8)
            fruit.velocity_y -= 8
            
            if spawn_count > 1:
                fruit.velocity_x += random.uniform(-2, 2)
            
            self.fruits.append(fruit)
    
    def trigger_screen_shake(self, intensity=5, duration=0.1):
        if not self.game_over:
            self.screen_shake = intensity
            self.shake_duration = duration
    
    def enter_frenzy_mode(self):
        self.frenzy_mode = True
        self.frenzy_timer = 8.0
        self.frenzy_count += 1
        self.spawn_interval = 0.5
    
    def end_frenzy_mode(self):
        self.frenzy_mode = False
        self.frenzy_cooldown = 3.0
        self.spawn_interval = 1.5
        
        base_requirement = 150
        scaling_factor = self.frenzy_count * 50
        self.next_frenzy_score = self.score + base_requirement + scaling_factor
    
    def detect_swipe(self, current_x, current_y):
        self.hand_history.append((current_x, current_y))
        if len(self.hand_history) > self.max_hand_history:
            self.hand_history.pop(0)
        
        if len(self.hand_history) >= 3:
            recent_start = self.hand_history[-3] if len(self.hand_history) >= 3 else self.hand_history[0]
            end_pos = self.hand_history[-1]
            distance = math.sqrt((end_pos[0] - recent_start[0])**2 + 
                               (end_pos[1] - recent_start[1])**2)
            
            if distance > self.swipe_threshold:
                return True
        
        return False
    
    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
            elif event.key == pygame.K_SPACE and not self.game_started and not self.game_over:
                self.game_started = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle score toggle click
            if self.score_toggle and self.score_toggle.is_clicked(event.pos, True):
                pass
            elif not self.game_started and not self.game_over:
                if self.start_button.is_clicked(event.pos, True):
                    self.game_started = True
            elif self.game_over:
                if self.reset_button_game_over.is_clicked(event.pos, True):
                    self.reset_game()
            else:
                if self.reset_button_normal.is_clicked(event.pos, True):
                    self.reset_game()
    
    def update_game(self):
        dt = 1/60
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Fallback to mouse position if hand tracking inactive
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Handle screen shake
        if not self.game_over and self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.screen_shake = 0
        elif self.game_over:
            self.screen_shake = 0
            self.shake_duration = 0
        
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        
        # Update score toggle (always active)
        if self.score_toggle:
            self.score_toggle.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Handle start screen
        if not self.game_started and not self.game_over:
            self.start_button.update(mouse_pos, hand_pos, hand_data.pinching)
            if self.start_button.is_hand_activated():
                self.game_started = True
            return  # Don't update game logic on start screen
        
        # Handle game over screen
        if self.game_over:
            self.reset_button_game_over.update(mouse_pos, hand_pos, hand_data.pinching)
            if self.reset_button_game_over.is_hand_activated():
                self.reset_game()
                return
            return  # Don't update game logic when game over
        
        # Handle normal gameplay - update reset button
        self.reset_button_normal.update(mouse_pos, hand_pos, hand_data.pinching)
        if self.reset_button_normal.is_hand_activated():
            self.reset_game()
            return
        
        # Game logic only runs if game started and not game over
        if not self.game_started:
            return
            
        # Update game timer
        self.game_time -= dt
        if self.game_time <= 0 or self.lives <= 0:
            self.game_over = True
            self.screen_shake = 0
            self.shake_duration = 0
            return
        
        # Handle frenzy mode
        if self.frenzy_mode:
            self.frenzy_timer -= dt
            if self.frenzy_timer <= 0:
                self.end_frenzy_mode()
        
        # Handle frenzy cooldown
        if self.frenzy_cooldown > 0:
            self.frenzy_cooldown -= dt
        
        # Check for frenzy mode trigger
        if (not self.frenzy_mode and self.frenzy_cooldown <= 0 and 
            self.score >= self.next_frenzy_score):
            self.enter_frenzy_mode()
        
        # Handle fruit spawning
        self.spawn_timer += dt
        current_spawn_interval = 0.3 if self.frenzy_mode else self.spawn_interval
        
        if self.spawn_timer >= current_spawn_interval:
            self.spawn_fruit()
            self.spawn_timer = 0
            if not self.frenzy_mode:
                self.spawn_interval = max(0.8, self.spawn_interval - 0.005)
        
        # Handle swipe detection
        is_swiping = self.detect_swipe(hand_data.x, hand_data.y)
        
        if is_swiping:
            self.swipe_trail.add_point(hand_data.x, hand_data.y)
            
            fruits_hit = 0
            bombs_hit = 0
            
            # Check collision with fruits
            for fruit in self.fruits[:]:
                if fruit.check_swipe_collision(self.swipe_trail.points):
                    score_gained = fruit.get_score()
                    self.score += score_gained
                    fruits_hit += 1
                    
                    if fruit.fruit_type == 'bomb':
                        bombs_hit += 1
                        
                        # Handle bomb hit
                        if self.frenzy_mode or self.frenzy_cooldown > 0:
                            # Protected mode - no life loss, just screen shake
                            self.trigger_screen_shake(15, 0.3)
                        else:
                            # Normal mode - lose life
                            self.lives -= 1
                            if self.lives <= 0:
                                self.game_over = True
                                self.screen_shake = 0
                                self.shake_duration = 0
                            else:
                                self.trigger_screen_shake(20, 0.5)
            
            # Handle combo system
            regular_fruits_hit = fruits_hit - bombs_hit
            if regular_fruits_hit > 1:
                self.combo_count += regular_fruits_hit
                self.combo_timer = 2.0
                # Bonus score for combo
                bonus_score = regular_fruits_hit * 10
                self.score += bonus_score
        else:
            # Clear swipe trail when not swiping
            if len(self.swipe_trail.points) > 0:
                self.swipe_trail.clear()
                self.hand_history = []
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
        
        # Update all fruits
        for fruit in self.fruits[:]:
            fruit.update(dt)
            
            # Remove fruits that are off screen
            if fruit.is_off_screen():
                # Only lose life if fruit was missed (not sliced and not bomb)
                if not fruit.sliced and fruit.fruit_type != 'bomb':
                    # Only lose life in normal mode (not during frenzy or cooldown)
                    if not self.frenzy_mode and self.frenzy_cooldown <= 0:
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_over = True
                            self.screen_shake = 0
                            self.shake_duration = 0
                self.fruits.remove(fruit)
    
    def draw_game(self):
        current_width, current_height = self.get_current_screen_size()
        
        # Handle screen shake
        shake_offset_x = 0
        shake_offset_y = 0
        
        if self.screen_shake > 0 and not self.game_over:
            shake_offset_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_offset_y = random.randint(-self.screen_shake, self.screen_shake)
        
        # Determine drawing surface
        if self.screen_shake > 0 and not self.game_over:
            temp_surface = pygame.Surface((current_width, current_height))
            draw_surface = temp_surface
        else:
            draw_surface = self.screen
        
        # Clear screen
        # draw_surface.fill(BLACK)
        
        # Draw background effects only during gameplay
        if self.game_started and not self.game_over:
            if self.frenzy_mode:
                frenzy_overlay = pygame.Surface((current_width, current_height))
                frenzy_overlay.set_alpha(30)
                frenzy_overlay.fill(RED)
                draw_surface.blit(frenzy_overlay, (0, 0))
            elif self.frenzy_cooldown > 0:
                cooldown_overlay = pygame.Surface((current_width, current_height))
                cooldown_overlay.set_alpha(20)
                cooldown_overlay.fill(BLUE)
                draw_surface.blit(cooldown_overlay, (0, 0))
        
        # Draw fruits only during gameplay
        if self.game_started and not self.game_over:
            for fruit in self.fruits:
                fruit.draw(draw_surface)
        
        # Draw swipe trail only during gameplay
        if self.game_started and not self.game_over:
            self.swipe_trail.draw(draw_surface)
        
        # Draw hand cursor (always visible when hand tracking is active)
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            if self.game_started and not self.game_over:
                cursor_color = YELLOW if len(self.swipe_trail.points) > 0 else GREEN
            else:
                cursor_color = WHITE  # Neutral color for menus
            pygame.draw.circle(draw_surface, cursor_color, (hand_data.x, hand_data.y), 12)
            pygame.draw.circle(draw_surface, WHITE, (hand_data.x, hand_data.y), 12, 3)
            
            # Show pinch indicator
            if hand_data.pinching:
                pygame.draw.circle(draw_surface, YELLOW, (hand_data.x, hand_data.y), 8)
        
        # Draw score toggle button (always visible)
        if self.score_toggle:
            self.score_toggle.draw(draw_surface, self.font_small)
        
        # Draw score panel (only if expanded and appropriate state)
        if self.score_toggle and (self.score_toggle.expanded or self.score_toggle.is_animating()):
            self.draw_simple_score_panel(draw_surface, current_width, current_height)
        
        # START SCREEN OVERLAY
        if not self.game_started and not self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(180)
            overlay.fill((20, 20, 40))  # Dark blue tint
            draw_surface.blit(overlay, (0, 0))
            
            # Title with glow effect
            title_text = self.font_title.render("SHOE SLASH CHALLENGE", True, YELLOW)
            title_shadow = self.font_title.render("SHOE SLASH CHALLENGE", True, (150, 150, 0))
            title_rect = title_text.get_rect(center=(current_width//2, current_height//2 - 120))
            shadow_rect = title_shadow.get_rect(center=(current_width//2 + 3, current_height//2 - 117))
            draw_surface.blit(title_shadow, shadow_rect)
            draw_surface.blit(title_text, title_rect)
            
            # Subtitle
            subtitle_text = self.font_medium.render("Slice fruits with hand gestures!", True, WHITE)
            subtitle_rect = subtitle_text.get_rect(center=(current_width//2, current_height//2 - 70))
            draw_surface.blit(subtitle_text, subtitle_rect)
            
            # Instructions
            instructions = [
                "• Move your hand to control the cursor",
                "• Pinch your fingers to interact with buttons", 
                "• Swipe through fruits to slice them",
                "• Avoid bombs or lose lives!"
            ]
            
            instruction_start_y = current_height//2 - 20
            for i, instruction in enumerate(instructions):
                text = self.font_small.render(instruction, True, LIGHT_GRAY)
                text_rect = text.get_rect(center=(current_width//2, instruction_start_y + i * 25))
                draw_surface.blit(text, text_rect)
            
            # Controls info
            controls_text = self.font_small.render("Controls: Hand Gestures or Mouse", True, (100, 200, 255))
            controls_rect = controls_text.get_rect(center=(current_width//2, current_height//2 + 80))
            draw_surface.blit(controls_text, controls_rect)
            
            # Start button
            self.start_button.draw(draw_surface, self.font_small)
            
            # Skip drawing game elements
            if self.screen_shake > 0:
                self.screen.fill(BLACK)
                self.screen.blit(temp_surface, (shake_offset_x, shake_offset_y))
            return
        
        # GAMEPLAY UI ELEMENTS
        if self.game_started and not self.game_over:
            # Combo indicator
            if self.combo_timer > 0:
                combo_color = YELLOW if not self.frenzy_mode else RED
                combo_text = self.font_title.render(f"COMBO x{self.combo_count}!", True, combo_color)
                combo_rect = combo_text.get_rect(center=(current_width//2, current_height//2 - 100))
                draw_surface.blit(combo_text, combo_rect)
            
            # Frenzy mode announcement
            if self.frenzy_mode and self.frenzy_timer > 6:
                frenzy_announce = self.font_title.render("FRENZY MODE!", True, YELLOW)
                frenzy_rect = frenzy_announce.get_rect(center=(current_width//2, current_height//2))
                
                # Pulse effect
                pulse = math.sin(self.frenzy_timer * 10) * 10
                frenzy_rect.y += int(pulse)
                draw_surface.blit(frenzy_announce, frenzy_rect)
            
            # Draw normal reset button
            self.reset_button_normal.draw(draw_surface, self.font_small)
            
            # Quick stats (when score panel is collapsed)
            if not (self.score_toggle and self.score_toggle.expanded):
                stats_y = current_height - 40
                quick_stats = f"Score: {self.score} | Lives: {self.lives} | Time: {self.game_time:.1f}s"
                if self.frenzy_mode:
                    quick_stats += f" | FRENZY: {self.frenzy_timer:.1f}s"
                elif self.frenzy_cooldown > 0:
                    quick_stats += f" | PROTECTED: {self.frenzy_cooldown:.1f}s"
                
                stats_text = self.font_small.render(quick_stats, True, WHITE)
                stats_rect = stats_text.get_rect(center=(current_width//2, stats_y))
                draw_surface.blit(stats_text, stats_rect)
        
        # GAME OVER SCREEN
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            draw_surface.blit(overlay, (0, 0))
            
            # Game Over title
            game_over_text = self.font_title.render("GAME OVER", True, RED)
            game_over_shadow = self.font_title.render("GAME OVER", True, (100, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(current_width//2, current_height//2 - 120))
            shadow_rect = game_over_shadow.get_rect(center=(current_width//2 + 2, current_height//2 - 118))
            draw_surface.blit(game_over_shadow, shadow_rect)
            draw_surface.blit(game_over_text, game_over_rect)
            
            # Final score
            final_score_text = self.font_title.render(f"Final Score: {self.score}", True, YELLOW)
            score_rect = final_score_text.get_rect(center=(current_width//2, current_height//2 - 70))
            draw_surface.blit(final_score_text, score_rect)
            
            # Performance message
            if self.score >= 3000:
                message = "NINJA MASTER! Incredible skills!"
                message_color = GREEN
            elif self.score >= 2000:
                message = "SHOE WARRIOR! Great job!"
                message_color = YELLOW
            elif self.score >= 800:
                message = "GOOD SLICING! Keep practicing!"
                message_color = (255, 165, 0)
            else:
                message = "Nice try! Swipe faster next time!"
                message_color = WHITE
            
            message_text = self.font_medium.render(message, True, message_color)
            message_rect = message_text.get_rect(center=(current_width//2, current_height//2 - 20))
            draw_surface.blit(message_text, message_rect)
            
            # Game stats
            stats = [
                f"Game Time: {60 - self.game_time:.1f} seconds",
                f"Fruits Sliced: {self.score // 20}",  # Rough estimate
                f"Frenzy Modes: {self.frenzy_count}"
            ]
            
            stats_start_y = current_height//2 + 20
            for i, stat in enumerate(stats):
                stat_text = self.font_small.render(stat, True, LIGHT_GRAY)
                stat_rect = stat_text.get_rect(center=(current_width//2, stats_start_y + i * 20))
                draw_surface.blit(stat_text, stat_rect)
            
            # Play Again button
            self.reset_button_game_over.draw(draw_surface, self.font_small)

        dev_text = "Developed and Maintained by GVI Development Team"
        dev_surface = self.font_small.render(dev_text, True, (128, 128, 128))  # Abu-abu
        dev_rect = dev_surface.get_rect()
        dev_rect.bottomright = (current_width - 10, current_height - 10)
        draw_surface.blit(dev_surface, dev_rect)
        # Apply screen shake effect
        if self.screen_shake > 0 and not self.game_over:
            self.screen.fill(BLACK)
            self.screen.blit(temp_surface, (shake_offset_x, shake_offset_y))

    def draw_simple_score_panel(self, surface, screen_width, screen_height):
        """Draw animated score panel with transparency"""
        if self.score_toggle.animation_progress <= 0.01:
            return  # Jangan draw jika panel tertutup
        
        # Panel dimensions
        panel_width = 280
        max_panel_height = 160 if self.game_started else 120
        
        # Animated height based on progress
        current_height = int(max_panel_height * self.score_toggle.animation_progress)
        
        panel_x = screen_width//2 - panel_width//2
        panel_y = 60
        
        # Create transparent surface
        panel_surface = pygame.Surface((panel_width, current_height), pygame.SRCALPHA)
        
        # Background dengan transparency yang smooth
        alpha = int(180 * self.score_toggle.animation_progress)
        background_color = (30, 30, 40, alpha)  # Dark blue dengan alpha
        
        # Draw rounded background
        pygame.draw.rect(panel_surface, background_color, (0, 0, panel_width, current_height), border_radius=12)
        
        # Border dengan glow effect
        border_alpha = int(255 * self.score_toggle.animation_progress)
        border_color = (100, 150, 255, border_alpha)
        pygame.draw.rect(panel_surface, border_color, (0, 0, panel_width, current_height), 3, border_radius=12)
        
        # Content hanya muncul jika animasi sudah cukup terbuka
        if self.score_toggle.animation_progress > 0.3:
            content_alpha = int(255 * min(1.0, (self.score_toggle.animation_progress - 0.3) / 0.7))
            
            content_x = 20
            content_y = 20
            line_height = 22
            
            if self.game_started and not self.game_over:
                # Gameplay stats
                title_color = (255, 220, 100, content_alpha)  # Gold dengan alpha
                title_text = "Game Status"
                title_surface = self.font_medium.render(title_text, True, title_color[:3])
                title_surface.set_alpha(content_alpha)
                panel_surface.blit(title_surface, (content_x, content_y))
                
                stats = [
                    f"Score: {self.score}",
                    f"Lives: {self.lives}",
                    f"Time: {self.game_time:.1f}s",
                ]
                
                if self.frenzy_mode:
                    stats.append(f"FRENZY: {self.frenzy_timer:.1f}s")
                elif self.frenzy_cooldown > 0:
                    stats.append(f"Protected: {self.frenzy_cooldown:.1f}s")
                
                # Progress bar untuk time
                time_progress = self.game_time / 60.0
                bar_width = panel_width - 40
                bar_height = 8
                bar_y = content_y + len(stats) * line_height + 35
                
                # Background bar
                bar_bg_color = (50, 50, 50, content_alpha)
                pygame.draw.rect(panel_surface, bar_bg_color[:3], (content_x, bar_y, bar_width, bar_height), border_radius=4)
                
                # Progress bar
                progress_width = int(bar_width * time_progress)
                if time_progress > 0.3:
                    bar_color = (100, 255, 100, content_alpha)  # Green
                elif time_progress > 0.15:
                    bar_color = (255, 255, 100, content_alpha)  # Yellow
                else:
                    bar_color = (255, 100, 100, content_alpha)  # Red
                    
                if progress_width > 0:
                    pygame.draw.rect(panel_surface, bar_color[:3], (content_x, bar_y, progress_width, bar_height), border_radius=4)
                
            elif self.game_over:
                # Game over stats
                title_color = (255, 100, 100, content_alpha)  # Red
                title_text = "Final Results"
                title_surface = self.font_medium.render(title_text, True, title_color[:3])
                title_surface.set_alpha(content_alpha)
                panel_surface.blit(title_surface, (content_x, content_y))
                
                stats = [
                    f"Final Score: {self.score}",
                    f"Time Survived: {60 - self.game_time:.1f}s",
                    f"Frenzy Modes: {self.frenzy_count}",
                    f"Fruits Sliced: {self.score // 20}"  # Rough estimate
                ]
            else:
                # Start screen info
                title_color = (100, 200, 255, content_alpha)  # Light blue
                title_text = "Game Rules"
                title_surface = self.font_medium.render(title_text, True, title_color[:3])
                title_surface.set_alpha(content_alpha)
                panel_surface.blit(title_surface, (content_x, content_y))
                
                stats = [
                    "60 seconds to slice fruits",
                    "5 lives, avoid bombs!",
                    "Frenzy mode = invincible",
                    "Swipe through fruits to slice"
                ]
            
            # Draw stats
            text_color = (220, 220, 220, content_alpha)
            for i, stat in enumerate(stats):
                stat_surface = self.font_small.render(stat, True, text_color[:3])
                stat_surface.set_alpha(content_alpha)
                panel_surface.blit(stat_surface, (content_x, content_y + (i + 1) * line_height))
        
        # Blit panel ke main surface
        surface.blit(panel_surface, (panel_x, panel_y))