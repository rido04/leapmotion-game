# games/object_catcher_game.py
"""
Object Catcher Game - Generic & Reusable
Catch falling good items, avoid bad items
Brand-agnostic design with JSON config support
"""

import pygame
import math
import random
import os
import json
from .base_game import BaseGame
from core import *


class CatchParticle:
    """Particle for catch effects"""
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 1.0
        self.size = random.randint(4, 8)
        
    def update(self, dt):
        self.x += self.velocity_x * 60 * dt
        self.y += self.velocity_y * 60 * dt
        self.velocity_y += 15 * dt  # Gravity
        self.velocity_x *= 0.95
        self.life -= 2 * dt
        
    def draw(self, screen):
        if self.life > 0:
            alpha_factor = max(0, self.life)
            size = max(1, int(self.size * alpha_factor))
            color = tuple(min(255, int(c * alpha_factor * 1.2)) for c in self.color)
            if size > 0:
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)


class CatchEffect:
    """Visual effect when catching items"""
    def __init__(self, x, y, color, effect_type="success"):
        self.particles = []
        self.life = 1.0
        self.effect_type = effect_type
        
        # Create particles
        particle_count = 12 if effect_type == "success" else 8
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            speed = random.uniform(2, 5) if effect_type == "success" else random.uniform(1, 3)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - random.uniform(1, 2)
            
            particle = CatchParticle(x, y, color, vel_x, vel_y)
            self.particles.append(particle)
    
    def update(self, dt):
        self.life -= 2 * dt
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
    
    def is_finished(self):
        return len(self.particles) == 0


class FallingObject:
    """Generic falling object"""
    def __init__(self, x, y, obj_type, config, screen_width, screen_height, image=None):
        self.x = x
        self.y = y
        self.obj_type = obj_type  # 'good', 'bad', 'bonus'
        self.config = config
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = image
        
        # Physics
        self.velocity_y = config.get('fall_speed', 3.0)
        self.velocity_x = random.uniform(-0.5, 0.5)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        
        # Visual
        self.size = config.get('size', 60)
        self.color = config.get('color_fallback', [200, 200, 200])
        self.points = config.get('points', 10)
        self.penalty = config.get('penalty', 0)
        
        # State
        self.caught = False
        self.catch_effect = None
        
        # Animation
        self.pulse = random.uniform(0, math.pi * 2)
        
    def update(self, dt):
        if not self.caught:
            self.y += self.velocity_y * 60 * dt
            self.x += self.velocity_x * 60 * dt
            self.rotation += self.rotation_speed
            self.pulse += 3 * dt
            
            # Keep within horizontal bounds
            if self.x < self.size:
                self.x = self.size
                self.velocity_x = abs(self.velocity_x)
            elif self.x > self.screen_width - self.size:
                self.x = self.screen_width - self.size
                self.velocity_x = -abs(self.velocity_x)
        
        # Update catch effect
        if self.catch_effect:
            self.catch_effect.update(dt)
            if self.catch_effect.is_finished():
                self.catch_effect = None
    
    def is_off_screen(self):
        return self.y > self.screen_height + 100
    
    def catch(self):
        """Mark object as caught"""
        if not self.caught:
            self.caught = True
            effect_color = self.color if self.obj_type == 'good' else (255, 100, 100)
            self.catch_effect = CatchEffect(self.x, self.y, effect_color, 
                                           "success" if self.obj_type == 'good' else "fail")
            return True
        return False
    
    def draw(self, screen):
        if self.caught:
            # Draw catch effect
            if self.catch_effect:
                self.catch_effect.draw(screen)
            return
        
        # Pulse effect
        pulse_scale = 1.0 + math.sin(self.pulse) * 0.05
        current_size = int(self.size * pulse_scale)
        
        if self.image:
            # Draw image
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            scaled_image = pygame.transform.scale(rotated_image, (current_size, current_size))
            image_rect = scaled_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(scaled_image, image_rect)
        else:
            # Draw fallback shape
            if self.obj_type == 'good':
                # Circle with gradient effect
                for i in range(3):
                    radius = current_size // 2 - i * 3
                    alpha = 200 - i * 50
                    color = tuple(min(255, c + i * 20) for c in self.color)
                    pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), current_size // 2, 2)
                
                # Shine effect
                shine_x = int(self.x - current_size // 6)
                shine_y = int(self.y - current_size // 6)
                pygame.draw.circle(screen, (255, 255, 255, 150), (shine_x, shine_y), current_size // 5)
                
            elif self.obj_type == 'bad':
                # X mark in circle
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size // 2)
                pygame.draw.circle(screen, (50, 50, 50), (int(self.x), int(self.y)), current_size // 2, 3)
                
                # Draw X
                margin = current_size // 4
                pygame.draw.line(screen, WHITE, 
                               (self.x - margin, self.y - margin),
                               (self.x + margin, self.y + margin), 5)
                pygame.draw.line(screen, WHITE,
                               (self.x + margin, self.y - margin),
                               (self.x - margin, self.y + margin), 5)
                
            elif self.obj_type == 'bonus':
                # Star shape with glow
                # Glow
                for i in range(3):
                    glow_size = current_size // 2 + (3 - i) * 8
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*self.color, 50 // (i + 1)), 
                                     (glow_size, glow_size), glow_size)
                    screen.blit(glow_surf, (self.x - glow_size, self.y - glow_size))
                
                # Star
                self.draw_star(screen, int(self.x), int(self.y), current_size // 2, self.rotation, self.color)
    
    def draw_star(self, screen, x, y, size, rotation, color):
        """Draw a star shape"""
        points = []
        for i in range(10):
            angle = math.radians(rotation + i * 36)
            radius = size if i % 2 == 0 else size * 0.5
            point_x = x + math.cos(angle) * radius
            point_y = y + math.sin(angle) * radius
            points.append((int(point_x), int(point_y)))
        
        if len(points) >= 6:
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)


class Basket:
    """Player controlled basket"""
    def __init__(self, x, y, width, height, image=None, color=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.target_x = x
        self.image = image
        self.color = color or [100, 150, 200]
        
        # Movement smoothing
        self.smooth_speed = 15
        
        # Trail effect
        self.trail_points = []
        self.max_trail = 5
        
    def update(self, dt, target_x):
        """Smooth movement toward target"""
        self.target_x = target_x
        
        # Smooth interpolation
        dx = self.target_x - self.x
        self.x += dx * self.smooth_speed * dt
        
        # Add to trail if moved significantly
        if len(self.trail_points) == 0 or abs(self.x - self.trail_points[-1][0]) > 5:
            self.trail_points.append((self.x, self.y))
            if len(self.trail_points) > self.max_trail:
                self.trail_points.pop(0)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                          self.width, self.height)
    
    def draw(self, screen):
        # Draw trail
        if len(self.trail_points) > 1:
            for i in range(len(self.trail_points) - 1):
                alpha = int((i / len(self.trail_points)) * 100)
                start = (int(self.trail_points[i][0]), int(self.trail_points[i][1]))
                end = (int(self.trail_points[i + 1][0]), int(self.trail_points[i + 1][1]))
                color = tuple(int(c * 0.7) for c in self.color)
                pygame.draw.line(screen, color, start, end, 3)
        
        # Draw basket
        rect = self.get_rect()
        
        if self.image:
            # Draw image
            scaled_image = pygame.transform.scale(self.image, (self.width, self.height))
            screen.blit(scaled_image, rect.topleft)
        else:
            # Draw fallback basket
            # Main body with gradient
            for i in range(self.height):
                alpha = 200 - int((i / self.height) * 50)
                gradient_color = tuple(max(0, c - int((i / self.height) * 50)) for c in self.color)
                pygame.draw.rect(screen, gradient_color, 
                               (rect.x, rect.y + i, self.width, 1))
            
            # Border
            pygame.draw.rect(screen, WHITE, rect, 3)
            
            # Handles
            handle_y = rect.y - 5
            # Left handle
            pygame.draw.arc(screen, WHITE, 
                           (rect.x - 10, handle_y - 10, 30, 20), 0, math.pi, 3)
            # Right handle
            pygame.draw.arc(screen, WHITE,
                           (rect.right - 20, handle_y - 10, 30, 20), 0, math.pi, 3)


class ScorePanel:
    """Toggleable score panel"""
    def __init__(self, x, y, width=280):
        self.x = x
        self.y = y
        self.width = width
        self.expanded = True
        self.hover = False
        self.animation_progress = 1.0
        self.target_progress = 1.0
        self.animation_speed = 4.0
        
        # Toggle button
        self.toggle_height = 30
        self.toggle_rect = pygame.Rect(x, y, width, self.toggle_height)
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.border_color = (100, 150, 255)
        
    def update(self, dt, mouse_pos, hand_pos, is_clicking):
        # Check hover
        check_pos = hand_pos if hand_pos else mouse_pos
        self.hover = self.toggle_rect.collidepoint(check_pos) if check_pos else False
        
        # Toggle on click
        if self.hover and is_clicking:
            self.expanded = not self.expanded
            self.target_progress = 1.0 if self.expanded else 0.0
        
        # Smooth animation
        if self.animation_progress < self.target_progress:
            self.animation_progress = min(self.target_progress, 
                                        self.animation_progress + self.animation_speed * dt)
        elif self.animation_progress > self.target_progress:
            self.animation_progress = max(self.target_progress, 
                                        self.animation_progress - self.animation_speed * dt)
    
    def draw(self, screen, game_data, fonts):
        """Draw score panel"""
        if self.animation_progress <= 0.01:
            # Just draw toggle button
            self.draw_toggle(screen, fonts['small'])
            return
        
        # Panel dimensions
        max_height = 200
        current_height = int(max_height * self.animation_progress)
        
        # Panel surface
        panel_surface = pygame.Surface((self.width, current_height + self.toggle_height), pygame.SRCALPHA)
        
        # Background
        alpha = int(180 * self.animation_progress)
        pygame.draw.rect(panel_surface, (*self.bg_color, alpha), 
                        (0, 0, self.width, current_height + self.toggle_height), 
                        border_radius=12)
        
        # Border
        pygame.draw.rect(panel_surface, self.border_color, 
                        (0, 0, self.width, current_height + self.toggle_height), 
                        3, border_radius=12)
        
        # Toggle button
        self.draw_toggle_on_surface(panel_surface, fonts['small'])
        
        # Content (if expanded enough)
        if self.animation_progress > 0.3:
            content_alpha = int(255 * min(1.0, (self.animation_progress - 0.3) / 0.7))
            
            y_offset = self.toggle_height + 15
            line_height = 25
            
            # Title
            title = fonts['medium'].render("Game Stats", True, (255, 220, 100))
            title.set_alpha(content_alpha)
            panel_surface.blit(title, (15, y_offset))
            y_offset += 35
            
            # Stats
            stats = [
                f"Score: {game_data['score']}",
                f"Lives: {game_data['lives']}",
                f"Caught: {game_data['caught']}",
                f"Combo: x{game_data['combo']}" if game_data['combo'] > 1 else "Combo: ---",
            ]
            
            if game_data.get('level'):
                stats.append(f"Level: {game_data['level']}")
            
            for stat in stats:
                stat_surf = fonts['small'].render(stat, True, (220, 220, 220))
                stat_surf.set_alpha(content_alpha)
                panel_surface.blit(stat_surf, (15, y_offset))
                y_offset += line_height
        
        # Blit to screen
        screen.blit(panel_surface, (self.x, self.y))
    
    def draw_toggle(self, screen, font):
        """Draw toggle button only"""
        color = (80, 80, 80) if self.hover else (60, 60, 60)
        pygame.draw.rect(screen, color, self.toggle_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.toggle_rect, 2, border_radius=8)
        
        text = "Hide Score ▼" if self.expanded else "Show Score ▶"
        text_surf = font.render(text, True, (220, 220, 220))
        text_rect = text_surf.get_rect(center=self.toggle_rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_toggle_on_surface(self, surface, font):
        """Draw toggle button on panel surface"""
        color = (80, 80, 80) if self.hover else (60, 60, 60)
        toggle_rect = pygame.Rect(0, 0, self.width, self.toggle_height)
        pygame.draw.rect(surface, color, toggle_rect, border_radius=8)
        
        text = "Hide Score ▼" if self.expanded else "Show Score ▶"
        text_surf = font.render(text, True, (220, 220, 220))
        text_rect = text_surf.get_rect(center=(self.width // 2, self.toggle_height // 2))
        surface.blit(text_surf, text_rect)


class ObjectCatcherGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Object Catcher")
        
        # Load config and assets
        self.load_game_config()
        
        # Game state
        self.game_started = False
        self.game_over = False
        self.reset_game()
        
        # Spawn timing
        self.spawn_timer = 0
        self.spawn_interval = 1.5
        
        # Difficulty
        self.current_fall_speed = 3.0
        
        # Create UI
        self.create_game_ui()
        
        print("Object Catcher Game initialized!")
    
    def load_game_config(self):
        """Load game configuration from JSON"""
        config_path = os.path.join("assets", "object-catcher", "game_config.json")
        
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                print(f"Config loaded from {config_path}")
        except FileNotFoundError:
            print(f"Config not found, using defaults")
            self.config = self.get_default_config()
        
        # Load assets
        self.load_assets()
    
    def get_default_config(self):
        """Default configuration"""
        return {
            "game_title": "Object Catcher",
            "basket": {
                "width": 120,
                "height": 60,
                "color_fallback": [100, 150, 200]
            },
            "good_items": [
                {"points": 10, "size": 50, "color_fallback": [100, 200, 100], "spawn_weight": 50},
                {"points": 20, "size": 60, "color_fallback": [100, 150, 255], "spawn_weight": 30},
                {"points": 30, "size": 70, "color_fallback": [255, 200, 100], "spawn_weight": 20}
            ],
            "bad_items": [
                {"penalty": -1, "size": 55, "color_fallback": [200, 50, 50], "spawn_weight": 100}
            ],
            "bonus_items": [
                {"points": 50, "size": 65, "color_fallback": [255, 215, 0], "spawn_weight": 100}
            ],
            "difficulty": {
                "initial_spawn_rate": 1.5,
                "min_spawn_rate": 0.6,
                "initial_fall_speed": 3.0,
                "speed_increment": 0.2,
                "bad_item_chance": 0.15,
                "bonus_item_chance": 0.05
            },
            "game_settings": {
                "game_duration": 60,
                "starting_lives": 3,
                "miss_penalty": True,
                "combo_enabled": True
            }
        }
    
    def load_assets(self):
        """Load game assets"""
        self.assets = {
            'basket_image': None,
            'good_items': [],
            'bad_items': [],
            'bonus_items': []
        }
        
        # Try to load basket image
        basket_config = self.config.get('basket', {})
        basket_path = basket_config.get('image')
        if basket_path:
            try:
                full_path = os.path.join('assets', 'object-catcher', basket_path)
                self.assets['basket_image'] = pygame.image.load(full_path).convert_alpha()
            except:
                print(f"Basket image not found: {basket_path}")
        
        # Load item images
        for item_type in ['good_items', 'bad_items', 'bonus_items']:
            items_config = self.config.get(item_type, [])
            for item_config in items_config:
                image_path = item_config.get('image')
                image = None
                if image_path:
                    try:
                        full_path = os.path.join('assets', 'object-catcher', image_path)
                        image = pygame.image.load(full_path).convert_alpha()
                        size = item_config.get('size', 60)
                        image = pygame.transform.scale(image, (size, size))
                    except:
                        print(f"Item image not found: {image_path}")
                
                self.assets[item_type].append({
                    'image': image,
                    'config': item_config
                })
    
    def create_game_ui(self):
        """Create UI elements"""
        current_width, current_height = self.get_current_screen_size()
        
        # Score panel
        panel_x = current_width // 2 - 140
        self.score_panel = ScorePanel(panel_x, 20)
        
        # Buttons
        self.start_button = AnimatedButton(
            current_width // 2 - 90, current_height // 2 + 80,
            150, 60, "START", GREEN_DARK, BLACK
        )
        
        self.reset_button = AnimatedButton(
            current_width - 150, 20, 130, 50, "Reset", (255, 165, 0), BLACK
        )
        
        self.play_again_button = AnimatedButton(
            current_width // 2 - 90, current_height // 2 + 150,
            180, 60, "Play Again", GREEN_DARK, BLACK
        )
    
    def get_game_info(self):
        return {
            'name': self.config.get('game_title', 'Object Catcher'),
            'description': 'Catch falling objects with your basket',
            'preview_color': (100, 200, 150)
        }
    
    def reset_game(self):
        """Reset game state"""
        settings = self.config.get('game_settings', {})
        difficulty = self.config.get('difficulty', {})
        
        self.score = 0
        self.lives = settings.get('starting_lives', 3)
        self.game_time = settings.get('game_duration', 60)
        self.caught_count = 0
        self.missed_count = 0
        self.combo = 0
        self.max_combo = 0
        
        self.game_started = False
        self.game_over = False
        
        self.objects = []
        self.effects = []
        
        self.spawn_timer = 0
        self.spawn_interval = difficulty.get('initial_spawn_rate', 1.5)
        self.current_fall_speed = difficulty.get('initial_fall_speed', 3.0)
        
        # Create basket
        current_width, current_height = self.get_current_screen_size()
        basket_config = self.config.get('basket', {})
        basket_y = current_height - 100
        
        self.basket = Basket(
            current_width // 2, basket_y,
            basket_config.get('width', 120),
            basket_config.get('height', 60),
            self.assets.get('basket_image'),
            basket_config.get('color_fallback', [100, 150, 200])
        )
        
        # Track last pinch state
        self.last_pinch = False
    
    def spawn_object(self):
        """Spawn a new falling object"""
        current_width, current_height = self.get_current_screen_size()
        difficulty = self.config.get('difficulty', {})
        
        # Determine object type
        rand = random.random()
        bad_chance = difficulty.get('bad_item_chance', 0.15)
        bonus_chance = difficulty.get('bonus_item_chance', 0.05)
        
        if rand < bonus_chance and self.assets['bonus_items']:
            # Bonus item
            obj_type = 'bonus'
            item_data = random.choice(self.assets['bonus_items'])
        elif rand < bonus_chance + bad_chance and self.assets['bad_items']:
            # Bad item
            obj_type = 'bad'
            item_data = random.choice(self.assets['bad_items'])
        else:
            # Good item (weighted random)
            obj_type = 'good'
            if self.assets['good_items']:
                # Weighted selection
                weights = [item['config'].get('spawn_weight', 50) for item in self.assets['good_items']]
                item_data = random.choices(self.assets['good_items'], weights=weights)[0]
            else:
                return
        
        # Create object
        x = random.randint(50, current_width - 50)
        y = -50
        
        config = item_data['config'].copy()
        config['fall_speed'] = self.current_fall_speed
        
        obj = FallingObject(x, y, obj_type, config, current_width, current_height, item_data['image'])
        self.objects.append(obj)
    
    def check_collision(self):
        """Check for basket-object collisions"""
        basket_rect = self.basket.get_rect()
        
        for obj in self.objects[:]:
            if obj.caught:
                continue
            
            # Simple rect collision
            obj_rect = pygame.Rect(obj.x - obj.size // 2, obj.y - obj.size // 2, obj.size, obj.size)
            
            if basket_rect.colliderect(obj_rect):
                obj.catch()
                
                if obj.obj_type == 'good' or obj.obj_type == 'bonus':
                    # Good catch
                    self.score += obj.points
                    self.caught_count += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    
                    # Combo bonus
                    if self.combo > 1:
                        bonus = obj.points * (self.combo - 1) // 2
                        self.score += bonus
                        
                elif obj.obj_type == 'bad':
                    # Bad catch
                    self.lives -= 1
                    self.combo = 0
                    
                    if self.lives <= 0:
                        self.game_over = True
    
    def handle_game_events(self, event):
        """Handle game events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
            elif event.key == pygame.K_SPACE and not self.game_started and not self.game_over:
                self.game_started = True
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.game_started and not self.game_over:
                if self.start_button.is_clicked(event.pos, True):
                    self.game_started = True
            elif self.game_over:
                if self.play_again_button.is_clicked(event.pos, True):
                    self.reset_game()
            else:
                if self.reset_button.is_clicked(event.pos, True):
                    self.reset_game()
    
    def update_game(self):
        """Update game state"""
        dt = 1/60
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Fallback to mouse if no hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        
        # Update UI
        game_data = {
            'score': self.score,
            'lives': self.lives,
            'caught': self.caught_count,
            'combo': self.combo
        }
        self.score_panel.update(dt, mouse_pos, hand_pos, hand_data.pinching and not self.last_pinch)
        self.last_pinch = hand_data.pinching
        
        # Handle different states
        if not self.game_started and not self.game_over:
            self.start_button.update(mouse_pos, hand_pos, hand_data.pinching)
            if self.start_button.is_hand_activated():
                self.game_started = True
            return
        
        if self.game_over:
            self.play_again_button.update(mouse_pos, hand_pos, hand_data.pinching)
            if self.play_again_button.is_hand_activated():
                self.reset_game()
            return
        
        # Game running
        self.reset_button.update(mouse_pos, hand_pos, hand_data.pinching)
        if self.reset_button.is_hand_activated():
            self.reset_game()
            return
        
        # Update game timer
        self.game_time -= dt
        if self.game_time <= 0:
            self.game_over = True
            return
        
        # Update basket position
        self.basket.update(dt, hand_data.x)
        
        # Spawn objects
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_object()
            self.spawn_timer = 0
            
            # Progressive difficulty
            difficulty = self.config.get('difficulty', {})
            min_spawn = difficulty.get('min_spawn_rate', 0.6)
            self.spawn_interval = max(min_spawn, self.spawn_interval - 0.02)
            
            speed_increment = difficulty.get('speed_increment', 0.2)
            self.current_fall_speed += speed_increment * 0.1
        
        # Update objects
        for obj in self.objects[:]:
            obj.update(dt)
            
            # Remove off-screen objects
            if obj.is_off_screen():
                # Miss penalty for good items
                if not obj.caught and obj.obj_type in ['good', 'bonus']:
                    settings = self.config.get('game_settings', {})
                    if settings.get('miss_penalty', True):
                        self.lives -= 1
                        self.combo = 0
                        self.missed_count += 1
                        
                        if self.lives <= 0:
                            self.game_over = True
                
                self.objects.remove(obj)
        
        # Check collisions
        self.check_collision()
        
        # Update effects
        for effect in self.objects:
            if effect.catch_effect:
                effect.catch_effect.update(dt)
    
    def draw_game(self):
        """Draw game elements"""
        current_width, current_height = self.get_current_screen_size()
        
        # Draw objects
        for obj in self.objects:
            obj.draw(self.screen)
        
        # Draw basket
        self.basket.draw(self.screen)
        
        # Draw hand indicator
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            cursor_color = GREEN if not hand_data.pinching else YELLOW
            pygame.draw.circle(self.screen, cursor_color, (hand_data.x, hand_data.y), 12)
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), 12, 3)
        
        # Draw score panel
        game_data = {
            'score': self.score,
            'lives': self.lives,
            'caught': self.caught_count,
            'combo': self.combo
        }
        fonts = {
            'small': self.font_small,
            'medium': self.font_medium,
            'large': self.font_large
        }
        self.score_panel.draw(self.screen, game_data, fonts)
        
        # START SCREEN
        if not self.game_started and not self.game_over:
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(180)
            overlay.fill((20, 25, 35))
            self.screen.blit(overlay, (0, 0))
            
            # Title
            title = self.font_title.render(self.config.get('game_title', 'OBJECT CATCHER'), True, YELLOW)
            title_shadow = self.font_title.render(self.config.get('game_title', 'OBJECT CATCHER'), True, (150, 150, 0))
            title_rect = title.get_rect(center=(current_width // 2, current_height // 2 - 120))
            shadow_rect = title_shadow.get_rect(center=(current_width // 2 + 3, current_height // 2 - 117))
            self.screen.blit(title_shadow, shadow_rect)
            self.screen.blit(title, title_rect)
            
            # Subtitle
            subtitle = self.font_medium.render("Catch the falling objects!", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(current_width // 2, current_height // 2 - 70))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Instructions
            instructions = [
                "Move hand/mouse to control basket",
                "Catch good items, avoid bad ones!",
                "Build combos for bonus points"
            ]
            
            y_offset = current_height // 2 - 20
            for i, text in enumerate(instructions):
                inst = self.font_small.render(text, True, WHITE)
                inst_rect = inst.get_rect(center=(current_width // 2, y_offset + i * 25))
                self.screen.blit(inst, inst_rect)
            
            # Start button
            self.start_button.draw(self.screen, self.font_medium)
            return
        
        # GAMEPLAY HUD
        if self.game_started and not self.game_over:
            # Lives indicator
            lives_x = 20
            lives_y = current_height - 50
            lives_text = self.font_medium.render("Lives:", True, WHITE)
            self.screen.blit(lives_text, (lives_x, lives_y))
            
            heart_x = lives_x + 80
            for i in range(self.lives):
                pygame.draw.circle(self.screen, (255, 100, 100), (heart_x + i * 35, lives_y + 15), 12)
            
            # Combo indicator (if active)
            if self.combo > 1:
                combo_text = self.font_large.render(f"COMBO x{self.combo}!", True, YELLOW)
                combo_rect = combo_text.get_rect(center=(current_width // 2, current_height // 2 - 100))
                
                # Pulsing effect
                pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
                combo_rect.y += int(pulse)
                
                self.screen.blit(combo_text, combo_rect)
            
            # Timer
            timer_text = self.font_medium.render(f"Time: {int(self.game_time)}s", True, WHITE)
            timer_rect = timer_text.get_rect(topright=(current_width - 20, current_height - 50))
            self.screen.blit(timer_text, timer_rect)
            
            # Reset button
            self.reset_button.draw(self.screen, self.font_small)
        
        # GAME OVER SCREEN
        if self.game_over:
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(200)
            overlay.fill((20, 20, 40))
            self.screen.blit(overlay, (0, 0))
            
            # Game Over text
            game_over_text = self.font_title.render("GAME OVER", True, RED)
            game_over_shadow = self.font_title.render("GAME OVER", True, (100, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(current_width // 2, current_height // 2 - 190))
            shadow_rect = game_over_shadow.get_rect(center=(current_width // 2 + 2, current_height // 2 - 188))
            self.screen.blit(game_over_shadow, shadow_rect)
            self.screen.blit(game_over_text, game_over_rect)
            
            # Final score
            final_score = self.font_large.render(f"Final Score: {self.score}", True, YELLOW)
            score_rect = final_score.get_rect(center=(current_width // 2, current_height // 2 - 100))
            self.screen.blit(final_score, score_rect)
            
            # Stats
            stats = [
                f"Items Caught: {self.caught_count}",
                f"Items Missed: {self.missed_count}",
                f"Max Combo: x{self.max_combo}",
                f"Time Survived: {60 - int(self.game_time)}s"
            ]
            
            y_offset = current_height // 2 - 30
            for i, stat in enumerate(stats):
                stat_text = self.font_medium.render(stat, True, WHITE)
                stat_rect = stat_text.get_rect(center=(current_width // 2, y_offset + i * 30))
                self.screen.blit(stat_text, stat_rect)
            
            # Performance message
            if self.score >= 8000:
                message = "AMAZING! Perfect catcher!"
                msg_color = GREEN
            elif self.score >= 4000:
                message = "GREAT! Nice catching skills!"
                msg_color = YELLOW
            elif self.score >= 2000:
                message = "GOOD! Keep practicing!"
                msg_color = CYAN
            else:
                message = "Nice try! Try again!"
                msg_color = WHITE
            
            msg_text = self.font_medium.render(message, True, msg_color)
            msg_rect = msg_text.get_rect(center=(current_width // 2, current_height // 2 + 100))
            self.screen.blit(msg_text, msg_rect)
            
            # Play again button
            self.play_again_button.draw(self.screen, self.font_medium)
        
        # Developer credit
        dev_text = "Developed by GVI PT. Maxima Cipta Miliardatha Development Team"
        dev_surface = self.font_small.render(dev_text, True, (180, 180, 180))
        dev_rect = dev_surface.get_rect()
        dev_rect.bottomright = (current_width - 10, current_height - 10)
        self.screen.blit(dev_surface, dev_rect)
    
    def recalculate_game_layout(self):
        """Recalculate layout on resolution change"""
        self.create_game_ui()
        
        # Update basket position
        if hasattr(self, 'basket'):
            current_width, current_height = self.get_current_screen_size()
            self.basket.y = current_height - 100
            
        # Update objects screen dimensions
        if hasattr(self, 'objects'):
            current_width, current_height = self.get_current_screen_size()
            for obj in self.objects:
                obj.screen_width = current_width
                obj.screen_height = current_height