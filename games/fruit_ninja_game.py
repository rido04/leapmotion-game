# games/fruit_ninja_game.py
"""
Fruit Ninja style game with hand tracking - Perfect for Leap Motion Gen 1
Designed for Adidas outlets with swipe gestures
Fixed fullscreen layout alignment issues
"""

import pygame
import math
import random
from .base_game import BaseGame
from core import *


class Particle:
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 1.0
        self.size = random.randint(3, 8)
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.3  # Gravity
        self.life -= 0.02
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(self.life * 255)
            size = int(self.size * self.life)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class SwipeTrail:
    def __init__(self):
        self.points = []
        self.max_points = 20
        
    def add_point(self, x, y):
        self.points.append((x, y))
        if len(self.points) > self.max_points:
            self.points.pop(0)
    
    def clear(self):
        self.points = []
    
    def draw(self, screen):
        if len(self.points) > 1:
            for i in range(len(self.points) - 1):
                alpha = int((i / len(self.points)) * 255)
                thickness = max(1, int((i / len(self.points)) * 8))
                color = (*WHITE, alpha)
                
                start_pos = self.points[i]
                end_pos = self.points[i + 1]
                pygame.draw.line(screen, WHITE, start_pos, end_pos, thickness)


class FruitObject:
    def __init__(self, x, y, fruit_type, screen_width, screen_height):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.fruit_type = fruit_type  # 'apple', 'orange', 'banana', 'bomb'
        
        # Store screen dimensions for boundary checking
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Physics - Balanced throw that stays on screen
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-20, -15)  # Strong but controlled throw
        self.gravity = 0.45
        self.rotation = 0
        self.rotation_speed = random.uniform(-8, 8)
        
        # Visual
        self.sliced = False
        self.slice_angle = 0
        self.size = 40 if fruit_type != 'bomb' else 35
        self.particles = []
        
        # Fruit properties
        self.fruit_colors = {
            'apple': RED,
            'orange': (255, 165, 0),  # Orange
            'banana': YELLOW,
            'bomb': (64, 64, 64)  # Dark gray
        }
        
        # Scoring - Bombs give points in frenzy mode
        self.points = {
            'apple': 10,
            'orange': 15,
            'banana': 20,
            'bomb': 25  # Bombs give points instead of penalty in frenzy
        }
        
    def update(self):
        if not self.sliced:
            # Update position
            self.x += self.velocity_x
            self.y += self.velocity_y
            self.velocity_y += self.gravity
            self.rotation += self.rotation_speed
        
        # Update particles after slicing
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def is_off_screen(self):
        return (self.y > self.screen_height + 100 or 
                self.x < -100 or self.x > self.screen_width + 100)
    
    def check_swipe_collision(self, trail_points):
        """Check if swipe trail intersects with fruit"""
        if self.sliced or len(trail_points) < 2:
            return False
            
        fruit_rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, 
                                self.size, self.size)
        
        # Check if any trail segment intersects with fruit
        for i in range(len(trail_points) - 1):
            x1, y1 = trail_points[i]
            x2, y2 = trail_points[i + 1]
            
            # Simple line-circle intersection
            if self.line_circle_collision(x1, y1, x2, y2, self.x, self.y, self.size//2):
                self.slice(x1, y1, x2, y2)
                return True
        
        return False
    
    def line_circle_collision(self, x1, y1, x2, y2, cx, cy, radius):
        """Check collision between line segment and circle"""
        # Distance from center to line
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
        """Slice the fruit and create particles"""
        if self.sliced:
            return
            
        self.sliced = True
        self.slice_angle = math.atan2(y2 - y1, x2 - x1)
        
        # Create slice particles
        color = self.fruit_colors[self.fruit_type]
        for i in range(15):
            vel_x = random.uniform(-8, 8)
            vel_y = random.uniform(-10, -2)
            particle = Particle(self.x, self.y, color, vel_x, vel_y)
            self.particles.append(particle)
    
    def get_score(self):
        """Get score value for this fruit"""
        if self.fruit_type == 'bomb':
            return 25  # Bombs always give points now (for frenzy mode)
        return self.points.get(self.fruit_type, 0)
    
    def draw(self, screen):
        # Draw particles first
        for particle in self.particles:
            particle.draw(screen)
        
        if not self.sliced:
            # Draw whole fruit
            color = self.fruit_colors[self.fruit_type]
            
            # Draw fruit body
            if self.fruit_type == 'bomb':
                # Draw bomb
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size, 3)
                
                # Draw fuse
                fuse_x = int(self.x + math.cos(self.rotation * 0.1) * self.size * 0.8)
                fuse_y = int(self.y + math.sin(self.rotation * 0.1) * self.size * 0.8)
                pygame.draw.line(screen, YELLOW, (int(self.x), int(self.y)), (fuse_x, fuse_y), 4)
                pygame.draw.circle(screen, YELLOW, (fuse_x, fuse_y), 5)
            else:
                # Draw regular fruit
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
                
                # Add fruit details
                if self.fruit_type == 'apple':
                    # Apple stem
                    stem_x = int(self.x + math.cos(self.rotation * 0.1) * 5)
                    stem_y = int(self.y - self.size + 5)
                    pygame.draw.circle(screen, (139, 69, 19), (stem_x, stem_y), 3)
                elif self.fruit_type == 'banana':
                    # Banana curve
                    pygame.draw.arc(screen, (139, 69, 19), 
                                  (int(self.x - self.size), int(self.y - self.size//2), 
                                   self.size * 2, self.size), 0, math.pi, 3)
        else:
            # Draw sliced fruit halves
            color = self.fruit_colors[self.fruit_type]
            half_size = self.size // 2
            
            # Calculate slice positions
            offset_x = math.cos(self.slice_angle) * 20
            offset_y = math.sin(self.slice_angle) * 20
            
            # Draw two halves
            pygame.draw.circle(screen, color, 
                             (int(self.x - offset_x), int(self.y - offset_y)), half_size)
            pygame.draw.circle(screen, color, 
                             (int(self.x + offset_x), int(self.y + offset_y)), half_size)


class FruitNinjaGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Fruit Slash Challenge")
        
        # Hand tracking for swipe - initialize before reset_game()
        self.swipe_trail = SwipeTrail()
        self.hand_history = []
        self.max_hand_history = 10
        self.swipe_threshold = 15  # Minimum movement to register swipe
        
        # Screen shake effect
        self.screen_shake = 0
        self.shake_duration = 0
        
        # Game state
        self.reset_game()
        
        # Spawn timing
        self.spawn_timer = 0
        self.spawn_interval = 1.5  # seconds between spawns
        
        # Visual effects
        self.combo_timer = 0
        self.combo_count = 0
        self.last_combo_time = 0
        
        # Buttons - initialize positions dynamically
        self.create_game_buttons()
    
    def create_game_buttons(self):
        """Create game-specific buttons with dynamic positioning"""
        current_width, current_height = self.get_current_screen_size()
        
        self.reset_button_normal = AnimatedButton(
            current_width - 580, 20, 120, 50, "Reset", (255, 165, 0), (255, 200, 100)
        )
        self.reset_button_game_over = AnimatedButton(
            current_width//2 - 75, current_height//2 + 80, 150, 60, "Play Again", (255, 165, 0), (255, 200, 100)
        )
    
    def recalculate_game_layout(self):
        """Recalculate game-specific layout when screen size changes"""
        print("Recalculating Fruit Ninja layout...")
        self.create_game_buttons()
        
        # Update existing fruits with new screen dimensions
        current_width, current_height = self.get_current_screen_size()
        for fruit in self.fruits:
            fruit.screen_width = current_width
            fruit.screen_height = current_height
    
    def get_game_info(self):
        return {
            'name': 'Fruit Slash',
            'description': 'Slice fruits with hand gestures',
            'preview_color': (255, 165, 0)  # Orange
        }
    
    def reset_game(self):
        """Reset game state"""
        self.score = 0
        self.lives = 5  # Increased from 3 to 5 lives
        self.game_time = 60.0  # 1 minute game
        self.game_over = False
        self.fruits = []
        self.particles = []
        self.combo_count = 0
        self.combo_timer = 0
        self.spawn_timer = 0
        
        # Reset screen shake when resetting game
        self.screen_shake = 0
        self.shake_duration = 0
        
        # Frenzy mode
        self.frenzy_mode = False
        self.frenzy_timer = 0
        self.frenzy_cooldown = 0  # Cooldown after frenzy ends
        self.frenzy_threshold = 100  # Score to trigger frenzy
        self.next_frenzy_score = self.frenzy_threshold
        self.frenzy_count = 0  # Track how many frenzies triggered
        
        # Multi-spawn system
        self.multi_spawn_chance = 0.3  # 30% chance for multi-spawn
        
        # Clear tracking data only if they exist
        if hasattr(self, 'swipe_trail'):
            self.swipe_trail.clear()
        if hasattr(self, 'hand_history'):
            self.hand_history = []
    
    def spawn_fruit(self):
        """Spawn new fruit from bottom of screen"""
        current_width, current_height = self.get_current_screen_size()
        
        # Determine how many fruits to spawn
        if self.frenzy_mode:
            # In frenzy mode, spawn more fruits
            spawn_count = random.randint(2, 4)
        elif random.random() < self.multi_spawn_chance:
            # Regular multi-spawn
            spawn_count = random.randint(2, 3)
        else:
            # Single fruit
            spawn_count = 1
        
        for _ in range(spawn_count):
            # Random spawn position at bottom using dynamic screen width
            spawn_x = random.randint(80, current_width - 80)
            spawn_y = current_height + 20
            
            # Choose fruit type
            if self.frenzy_mode:
                # More fruits, fewer bombs in frenzy
                fruit_types = ['apple', 'orange', 'banana']
                if random.random() < 0.1:  # Only 10% bombs in frenzy
                    fruit_type = 'bomb'
                else:
                    fruit_type = random.choice(fruit_types)
            else:
                # Normal spawn rates
                fruit_types = ['apple', 'orange', 'banana']
                if random.random() < 0.2:  # 20% chance for bomb
                    fruit_type = 'bomb'
                else:
                    fruit_type = random.choice(fruit_types)
            
            fruit = FruitObject(spawn_x, spawn_y, fruit_type, current_width, current_height)
            # Add controlled boost - prevent flying off screen
            extra_boost = random.uniform(1, 3) if not self.frenzy_mode else random.uniform(2, 5)
            fruit.velocity_y -= extra_boost
            
            # Spread fruits horizontally for multi-spawn
            if spawn_count > 1:
                fruit.velocity_x += random.uniform(-2, 2)
            
            self.fruits.append(fruit)
    
    def trigger_screen_shake(self, intensity=10, duration=0.3):
        """Trigger screen shake effect"""
        # Don't trigger screen shake if game is over
        if not self.game_over:
            self.screen_shake = intensity
            self.shake_duration = duration
    
    def enter_frenzy_mode(self):
        """Enter frenzy mode"""
        self.frenzy_mode = True
        self.frenzy_timer = 8.0  # 8 seconds of frenzy
        self.frenzy_count += 1
        self.spawn_interval = 0.5  # Much faster spawning
        print("FRENZY MODE ACTIVATED!")
    
    def end_frenzy_mode(self):
        """End frenzy mode and start cooldown"""
        self.frenzy_mode = False
        self.frenzy_cooldown = 3.0  # 3 second cooldown
        self.spawn_interval = 1.5  # Back to normal spawn rate
        
        # Calculate next frenzy requirement (increasing difficulty)
        base_requirement = 150
        scaling_factor = self.frenzy_count * 50  # Each frenzy makes next one harder
        self.next_frenzy_score = self.score + base_requirement + scaling_factor
        
        print(f"Frenzy mode ended! Cooldown: 3s | Next frenzy at: {self.next_frenzy_score} pts")
    
    def detect_swipe(self, current_x, current_y):
        """Detect if hand is making swipe motion"""
        # Add current position to history
        self.hand_history.append((current_x, current_y))
        if len(self.hand_history) > self.max_hand_history:
            self.hand_history.pop(0)
        
        # Check if we have enough movement for a swipe
        if len(self.hand_history) >= 3:
            start_pos = self.hand_history[0]
            end_pos = self.hand_history[-1]
            distance = math.sqrt((end_pos[0] - start_pos[0])**2 + 
                               (end_pos[1] - start_pos[1])**2)
            
            if distance > self.swipe_threshold:
                return True
        
        return False
    
    def handle_game_events(self, event):
        """Handle fruit ninja specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check which button to use based on game state
            if self.game_over:
                if self.reset_button_game_over.is_clicked(event.pos, True):
                    self.reset_game()
            else:
                if self.reset_button_normal.is_clicked(event.pos, True):
                    self.reset_game()
    
    def update_game(self):
        """Update fruit ninja game state"""
        dt = 1/60  # Assume 60 FPS
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if no hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Update screen shake only if game is not over
        if not self.game_over and self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.screen_shake = 0
        elif self.game_over:
            # Stop screen shake immediately when game over
            self.screen_shake = 0
            self.shake_duration = 0
        
        # Update buttons based on game state
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        
        if self.game_over:
            self.reset_button_game_over.update(mouse_pos, hand_pos, hand_data.pinching)
            if self.reset_button_game_over.is_hand_activated():
                self.reset_game()
                return
        else:
            self.reset_button_normal.update(mouse_pos, hand_pos, hand_data.pinching)
            if self.reset_button_normal.is_hand_activated():
                self.reset_game()
                return
        
        if self.game_over:
            return
            
        # Update game timer
        self.game_time -= dt
        if self.game_time <= 0 or self.lives <= 0:
            self.game_over = True
            # Stop screen shake when game ends
            self.screen_shake = 0
            self.shake_duration = 0
        
        # Update frenzy mode
        if self.frenzy_mode:
            self.frenzy_timer -= dt
            if self.frenzy_timer <= 0:
                self.end_frenzy_mode()
        
        # Update frenzy cooldown
        if self.frenzy_cooldown > 0:
            self.frenzy_cooldown -= dt
            if self.frenzy_cooldown <= 0:
                print("Frenzy cooldown ended! Ready for next frenzy!")
        
        # Check for frenzy trigger (only if not in frenzy and no cooldown)
        if (not self.frenzy_mode and self.frenzy_cooldown <= 0 and 
            self.score >= self.next_frenzy_score):
            self.enter_frenzy_mode()
        
        # Update spawn timer
        self.spawn_timer += dt
        current_spawn_interval = 0.3 if self.frenzy_mode else self.spawn_interval
        
        if self.spawn_timer >= current_spawn_interval:
            self.spawn_fruit()
            self.spawn_timer = 0
            # Gradually increase difficulty
            if not self.frenzy_mode:
                self.spawn_interval = max(0.8, self.spawn_interval - 0.005)
        
        # Handle swipe detection
        is_swiping = self.detect_swipe(hand_data.x, hand_data.y)
        
        if is_swiping:
            # Add to swipe trail
            self.swipe_trail.add_point(hand_data.x, hand_data.y)
            
            # Check fruit collisions
            fruits_hit = 0
            bombs_hit = 0
            
            for fruit in self.fruits[:]:
                if fruit.check_swipe_collision(self.swipe_trail.points):
                    score_gained = fruit.get_score()
                    self.score += score_gained
                    fruits_hit += 1
                    
                    if fruit.fruit_type == 'bomb':
                        bombs_hit += 1
                        
                        if self.frenzy_mode or self.frenzy_cooldown > 0:
                            # In frenzy mode OR cooldown period, bombs are safe
                            self.trigger_screen_shake(15, 0.3)
                            if self.frenzy_mode:
                                print(f"💣 FRENZY BOMB SLICE! +{score_gained} points! 🔥")
                            else:
                                print(f"💣 COOLDOWN PROTECTION! +{score_gained} points! 🛡️")
                        else:
                            # Normal mode - bombs are bad
                            self.lives -= 1
                            # Check if this causes game over
                            if self.lives <= 0:
                                self.game_over = True
                                # Stop screen shake immediately on game over
                                self.screen_shake = 0
                                self.shake_duration = 0
                                print(f"💣 BOMB HIT! Game Over! Final Score: {self.score}")
                            else:
                                # Only shake if game doesn't end
                                self.trigger_screen_shake(20, 0.5)
                                print(f"💣 BOMB HIT! Screen shake! Lives left: {self.lives}")
                    else:
                        print(f"Fruit sliced! Score: +{score_gained}")
            
            # Combo system
            regular_fruits_hit = fruits_hit - bombs_hit
            if regular_fruits_hit > 1:
                self.combo_count += regular_fruits_hit
                self.combo_timer = 2.0  # Show combo for 2 seconds
                bonus_score = regular_fruits_hit * 10  # Increased bonus
                self.score += bonus_score
                print(f"🔥 COMBO x{regular_fruits_hit}! Bonus: +{bonus_score}")
        else:
            # Clear trail when not swiping
            if len(self.swipe_trail.points) > 0:
                self.swipe_trail.clear()
                self.hand_history = []
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
        
        # Update fruits
        for fruit in self.fruits[:]:
            fruit.update()
            
            # Remove fruits that fell off screen
            if fruit.is_off_screen():
                if not fruit.sliced and fruit.fruit_type != 'bomb':
                    # Only lose life for missing fruits in normal mode (not during frenzy OR cooldown)
                    if not self.frenzy_mode and self.frenzy_cooldown <= 0:
                        self.lives -= 1  # Lost life for missing fruit
                        # Check if this causes game over
                        if self.lives <= 0:
                            self.game_over = True
                            # Stop screen shake immediately on game over
                            self.screen_shake = 0
                            self.shake_duration = 0
                        print(f"Fruit missed! Lives left: {self.lives}")
                    else:
                        if self.frenzy_mode:
                            print("Fruit missed but no penalty in frenzy mode!")
                        else:
                            print("Fruit missed but protected by cooldown!")
                self.fruits.remove(fruit)
    
    def draw_game(self):
        """Draw fruit ninja game elements"""
        current_width, current_height = self.get_current_screen_size()
        
        # Apply screen shake effect only if game is not over
        shake_offset_x = 0
        shake_offset_y = 0
        
        if self.screen_shake > 0 and not self.game_over:
            shake_offset_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_offset_y = random.randint(-self.screen_shake, self.screen_shake)
        
        # Create temporary surface for shake effect - Fixed: use dynamic screen size
        if self.screen_shake > 0 and not self.game_over:
            temp_surface = pygame.Surface((current_width, current_height))
            draw_surface = temp_surface
        else:
            draw_surface = self.screen
        
        # Draw background effect for frenzy mode
        if self.frenzy_mode and not self.game_over:
            # Red tinted overlay for frenzy - Fixed: use dynamic screen size
            frenzy_overlay = pygame.Surface((current_width, current_height))
            frenzy_overlay.set_alpha(30)
            frenzy_overlay.fill(RED)
            draw_surface.blit(frenzy_overlay, (0, 0))
        elif self.frenzy_cooldown > 0 and not self.game_over:
            # Blue tinted overlay for cooldown - Fixed: use dynamic screen size
            cooldown_overlay = pygame.Surface((current_width, current_height))
            cooldown_overlay.set_alpha(20)
            cooldown_overlay.fill(BLUE)
            draw_surface.blit(cooldown_overlay, (0, 0))
        
        # Draw title
        title_text = self.font_title.render("FRUIT SLASHER", True, WHITE)
        title_x = 250
        title_y = 40
        draw_surface.blit(title_text, (title_x, title_y))
        
        # Subtitle with mode indicator
        if self.frenzy_mode:
            subtitle_text = self.font_small.render("FRENZY MODE!", True, YELLOW)
        elif self.frenzy_cooldown > 0:
            subtitle_text = self.font_small.render("COOLDOWN PROTECTION", True, BLUE)
        else:
            subtitle_text = self.font_small.render("Swipe Challenge", True, (255, 165, 0))
        subtitle_x = title_x
        subtitle_y = title_y + 50
        draw_surface.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # Draw fruits
        for fruit in self.fruits:
            fruit.draw(draw_surface)
        
        # Draw swipe trail
        self.swipe_trail.draw(draw_surface)
        
        # Draw hand cursor
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            # Draw hand indicator
            cursor_color = YELLOW if len(self.swipe_trail.points) > 0 else GREEN
            pygame.draw.circle(draw_surface, cursor_color, (hand_data.x, hand_data.y), 8)
            pygame.draw.circle(draw_surface, WHITE, (hand_data.x, hand_data.y), 8, 2)
        
        # Game UI
        ui_y = 120
        
        # Score with frenzy multiplier
        score_color = YELLOW if not self.frenzy_mode else RED
        score_text = self.font_medium.render(f"Score: {self.score}", True, score_color)
        draw_surface.blit(score_text, (50, ui_y))
        
        # Lives
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, RED)
        draw_surface.blit(lives_text, (50, ui_y + 40))
        
        # Timer
        time_color = RED if self.game_time < 15 else WHITE
        time_text = self.font_medium.render(f"Time: {self.game_time:.1f}s", True, time_color)
        draw_surface.blit(time_text, (50, ui_y + 80))
        
        # Frenzy/Cooldown timer
        if self.frenzy_mode:
            frenzy_text = self.font_medium.render(f"🔥 Frenzy: {self.frenzy_timer:.1f}s", True, YELLOW)
            draw_surface.blit(frenzy_text, (50, ui_y + 120))
            
            # Invincible indicator
            invincible_text = self.font_small.render("INVINCIBLE! No life loss!", True, GREEN)
            draw_surface.blit(invincible_text, (50, ui_y + 145))
        elif self.frenzy_cooldown > 0:
            cooldown_text = self.font_medium.render(f"🛡️ Cooldown: {self.frenzy_cooldown:.1f}s", True, BLUE)
            draw_surface.blit(cooldown_text, (50, ui_y + 120))
            
            # Protection indicator
            protection_text = self.font_small.render("PROTECTED! Bombs safe!", True, CYAN)
            draw_surface.blit(protection_text, (50, ui_y + 145))
        else:
            # Next frenzy indicator
            remaining = self.next_frenzy_score - self.score
            if remaining > 0:
                frenzy_text = self.font_small.render(f"Next Frenzy: {remaining} pts", True, LIGHT_GRAY)
                draw_surface.blit(frenzy_text, (50, ui_y + 120))
        
        # Combo indicator - Fixed: use dynamic screen size
        if self.combo_timer > 0:
            combo_alpha = int((self.combo_timer / 2.0) * 255)
            combo_color = YELLOW if not self.frenzy_mode else RED
            combo_text = self.font_title.render(f"COMBO x{self.combo_count}!", True, combo_color)
            combo_rect = combo_text.get_rect(center=(current_width//2, current_height//2 - 100))
            draw_surface.blit(combo_text, combo_rect)
        
        # Frenzy mode announcement - Fixed: use dynamic screen size
        if self.frenzy_mode and self.frenzy_timer > 6:  # Show for first 2 seconds
            frenzy_announce = self.font_title.render("FRENZY MODE!", True, YELLOW)
            frenzy_rect = frenzy_announce.get_rect(center=(current_width//2, current_height//2))
            
            # Pulsing effect
            pulse = math.sin(self.frenzy_timer * 10) * 10
            frenzy_rect.y += int(pulse)
            draw_surface.blit(frenzy_announce, frenzy_rect)
        
        # Game over screen - Fixed: use dynamic screen size
        if self.game_over:
            overlay = pygame.Surface((current_width, current_height))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            draw_surface.blit(overlay, (0, 0))
            
            # Game Over Title
            game_over_text = self.font_title.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(current_width//2, current_height//2 - 100))
            draw_surface.blit(game_over_text, game_over_rect)
            
            # Final score
            final_score_text = self.font_title.render(f"Final Score: {self.score}", True, YELLOW)
            score_rect = final_score_text.get_rect(center=(current_width//2, current_height//2 - 50))
            draw_surface.blit(final_score_text, score_rect)
            
            # Performance message
            if self.score >= 3000:
                message = "NINJA MASTER! Incredible skills!"
                message_color = GREEN
            elif self.score >= 1500:
                message = "FRUIT WARRIOR! Great job!"
                message_color = YELLOW
            elif self.score >= 500:
                message = "GOOD SLICING! Keep practicing!"
                message_color = (255, 165, 0)
            else:
                message = "Nice try! Swipe faster next time!"
                message_color = WHITE
            
            message_text = self.font_medium.render(message, True, message_color)
            message_rect = message_text.get_rect(center=(current_width//2, current_height//2 + 20))
            draw_surface.blit(message_text, message_rect)
            
            # Draw game over reset button (centered)
            self.reset_button_game_over.draw(draw_surface, self.font_small)
        else:
            # Draw normal reset button (top right)
            self.reset_button_normal.draw(draw_surface, self.font_small)
        
        # Instructions - Fixed: use dynamic screen size
        if not self.game_over:
            instructions = [
                "SWIPE through fruits to slice them | FRENZY MODE = Invincible!",
                "After frenzy: 3s COOLDOWN protection | Bombs safe during both modes!",
                "R: Reset | ESC: Back to Menu"
            ]
            
            instruction_y = current_height - 80
            for i, instruction in enumerate(instructions):
                text = self.font_small.render(instruction, True, LIGHT_GRAY)
                text_rect = text.get_rect(center=(current_width//2, instruction_y + i * 25))
                draw_surface.blit(text, text_rect)
        
        # Blit shaken surface to main screen (only if not game over) - Fixed: use dynamic screen size
        if self.screen_shake > 0 and not self.game_over:
            self.screen.fill(BLACK)  # Clear main screen
            self.screen.blit(temp_surface, (shake_offset_x, shake_offset_y))