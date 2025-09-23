# games/archery_game.py
"""
Archery Game with hand tracking - Perfect for retail environments
Designed for Adidas outlets with brand integration
"""

import pygame
import math
import random
from .base_game import BaseGame
from core import *


class Arrow:
    def __init__(self, start_x, start_y, target_x, target_y, power):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        
        # Calculate trajectory
        distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
        self.velocity_x = (target_x - start_x) / distance * power * 8
        self.velocity_y = (target_y - start_y) / distance * power * 8
        
        # Physics
        self.gravity = 0.2
        self.active = True
        self.trail_points = []
        
    def update(self):
        if not self.active:
            return
            
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        
        # Add trail point
        self.trail_points.append((int(self.x), int(self.y)))
        if len(self.trail_points) > 15:
            self.trail_points.pop(0)
        
        # Check bounds
        if (self.x < 0 or self.x > WINDOW_WIDTH or 
            self.y < 0 or self.y > WINDOW_HEIGHT):
            self.active = False
    
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw trail
        for i, point in enumerate(self.trail_points):
            alpha = int((i / len(self.trail_points)) * 255)
            trail_color = (*WHITE, alpha)
            radius = max(1, i // 3)
            pygame.draw.circle(screen, WHITE, point, radius)
        
        # Draw arrow head
        if self.trail_points:
            # Calculate arrow rotation
            if len(self.trail_points) >= 2:
                dx = self.trail_points[-1][0] - self.trail_points[-2][0]
                dy = self.trail_points[-1][1] - self.trail_points[-2][1]
                angle = math.atan2(dy, dx)
                
                # Arrow head points
                head_length = 15
                head_width = 8
                
                # Calculate arrow head points
                tip_x = self.x
                tip_y = self.y
                
                left_x = tip_x - head_length * math.cos(angle - math.pi/6)
                left_y = tip_y - head_length * math.sin(angle - math.pi/6)
                
                right_x = tip_x - head_length * math.cos(angle + math.pi/6)
                right_y = tip_y - head_length * math.sin(angle + math.pi/6)
                
                # Draw arrow head
                pygame.draw.polygon(screen, YELLOW, [
                    (tip_x, tip_y),
                    (left_x, left_y), 
                    (right_x, right_y)
                ])


class Target:
    def __init__(self, x, y, size=80):
        self.x = x
        self.y = y
        self.size = size
        self.hit = False
        self.animation_scale = 1.0
        self.pulse_time = 0
        
        # Adidas branding
        self.rings = [
            (RED, size),
            (WHITE, size * 0.8),
            (RED, size * 0.6),
            (WHITE, size * 0.4),
            (RED, size * 0.2)
        ]
    
    def update(self, dt):
        self.pulse_time += dt
        if not self.hit:
            self.animation_scale = 1.0 + math.sin(self.pulse_time * 3) * 0.1
    
    def check_hit(self, arrow_x, arrow_y):
        if self.hit:
            return 0
            
        distance = math.sqrt((arrow_x - self.x)**2 + (arrow_y - self.y)**2)
        
        # Score based on accuracy
        if distance <= self.size * 0.2:  # Bullseye
            self.hit = True
            return 100
        elif distance <= self.size * 0.4:  # Inner ring
            self.hit = True
            return 50
        elif distance <= self.size * 0.6:  # Middle ring
            self.hit = True
            return 25
        elif distance <= self.size * 0.8:  # Outer ring
            self.hit = True
            return 10
        
        return 0
    
    def draw(self, screen):
        # Draw target rings
        for color, ring_size in self.rings:
            scaled_size = int(ring_size * self.animation_scale)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), scaled_size)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), scaled_size, 2)
        
        # Draw Adidas logo in center if not hit
        if not self.hit:
            # Simple 3-stripes representation
            stripe_width = 3
            stripe_height = int(self.size * 0.3)
            center_x = int(self.x)
            center_y = int(self.y)
            
            for i in range(3):
                stripe_x = center_x - stripe_width - stripe_width * i * 2
                pygame.draw.rect(screen, BLACK, 
                               (stripe_x, center_y - stripe_height//2, 
                                stripe_width, stripe_height))


class ArcheryGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Adidas Archery Challenge")
        
        # Game state
        self.reset_game()
        
        # Hand tracking state
        self.hand_start_pos = None
        self.is_drawing = False
        self.draw_power = 0
        self.max_draw_power = 1.0
        
        # Visual feedback
        self.crosshair_pulse = 0
        self.last_pinch = False
        
        # Timing for retail environment
        self.game_duration = 30  # 30 second sessions
        self.countdown_started = False
        
        # Buttons
        self.reset_button = AnimatedButton(
            WINDOW_WIDTH - 580, 20, 120, 50, "🎯 Reset", RED, (255, 100, 100)
        )
    
    def get_game_info(self):
        return {
            'name': 'Archery Challenge',
            'description': 'Test your precision with hand tracking',
            'preview_color': RED
        }
    
    def reset_game(self):
        """Reset game state for new player"""
        self.score = 0
        self.arrows_left = 5
        self.arrows_fired = []
        self.game_time = 30.0
        self.game_over = False
        self.countdown_started = False
        
        # Create targets at different distances
        self.targets = [
            Target(WINDOW_WIDTH * 0.8, WINDOW_HEIGHT * 0.3, 60),   # Top target
            Target(WINDOW_WIDTH * 0.85, WINDOW_HEIGHT * 0.5, 70),  # Center target  
            Target(WINDOW_WIDTH * 0.8, WINDOW_HEIGHT * 0.7, 65),   # Bottom target
        ]
        
        # Reset hand tracking state
        self.hand_start_pos = None
        self.is_drawing = False
        self.draw_power = 0
    
    def handle_game_events(self, event):
        """Handle archery specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_game()
            elif event.key == pygame.K_SPACE and self.arrows_left > 0:
                # Keyboard fallback - shoot arrow to center
                self.shoot_arrow(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2,
                               WINDOW_WIDTH * 0.85, WINDOW_HEIGHT * 0.5, 0.8)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.reset_button.is_clicked(event.pos, True):
                self.reset_game()
    
    def shoot_arrow(self, start_x, start_y, target_x, target_y, power):
        """Shoot an arrow"""
        if self.arrows_left > 0 and not self.game_over:
            arrow = Arrow(start_x, start_y, target_x, target_y, power)
            self.arrows_fired.append(arrow)
            self.arrows_left -= 1
            
            if not self.countdown_started:
                self.countdown_started = True
    
    def update_game(self):
        """Update archery game state"""
        dt = 1/60  # Assume 60 FPS
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if no hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Update game timer
        if self.countdown_started and not self.game_over:
            self.game_time -= dt
            if self.game_time <= 0 or self.arrows_left <= 0:
                self.game_over = True
        
        # Hand tracking for bow mechanics
        current_pos = (hand_data.x, hand_data.y)
        
        # Start drawing (pinch detected)
        if hand_data.pinching and not self.last_pinch and not self.is_drawing:
            self.hand_start_pos = current_pos
            self.is_drawing = True
            self.draw_power = 0
            print("Started drawing bow!")
        
        # Continue drawing
        elif hand_data.pinching and self.is_drawing and self.hand_start_pos:
            # Calculate draw distance
            draw_distance = math.sqrt(
                (current_pos[0] - self.hand_start_pos[0])**2 + 
                (current_pos[1] - self.hand_start_pos[1])**2
            )
            self.draw_power = min(draw_distance / 150.0, self.max_draw_power)
        
        # Release arrow (pinch released)
        elif not hand_data.pinching and self.last_pinch and self.is_drawing:
            if self.hand_start_pos and self.draw_power > 0.1:
                # Shoot arrow from bow position to current hand position
                bow_x = WINDOW_WIDTH * 0.15
                bow_y = WINDOW_HEIGHT * 0.5
                self.shoot_arrow(bow_x, bow_y, current_pos[0], current_pos[1], self.draw_power)
                print(f"Arrow released with power: {self.draw_power:.2f}")
            
            self.is_drawing = False
            self.hand_start_pos = None
            self.draw_power = 0
        
        self.last_pinch = hand_data.pinching
        
        # Update visual effects
        self.crosshair_pulse += dt * 5
        
        # Update arrows
        for arrow in self.arrows_fired[:]:
            arrow.update()
            
            # Check target hits
            for target in self.targets:
                if arrow.active:
                    score_gained = target.check_hit(arrow.x, arrow.y)
                    if score_gained > 0:
                        self.score += score_gained
                        arrow.active = False
                        print(f"Target hit! Score: +{score_gained}")
            
            # Remove inactive arrows
            if not arrow.active:
                if arrow in self.arrows_fired:
                    self.arrows_fired.remove(arrow)
        
        # Update targets
        for target in self.targets:
            target.update(dt)
        
        # Update reset button
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        self.reset_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        if self.reset_button.is_hand_activated():
            self.reset_game()
    
    def draw_bow(self):
        """Draw the bow and arrow being drawn"""
        bow_x = WINDOW_WIDTH * 0.15
        bow_y = WINDOW_HEIGHT * 0.5
        bow_size = 100
        
        # Draw bow
        bow_color = (139, 69, 19)  # Brown
        pygame.draw.arc(self.screen, bow_color, 
                       (bow_x - bow_size//2, bow_y - bow_size//2, bow_size, bow_size),
                       -math.pi/3, math.pi/3, 8)
        
        # Draw bow string
        string_top = (bow_x - 30, bow_y - 60)
        string_bottom = (bow_x - 30, bow_y + 60)
        pygame.draw.line(self.screen, WHITE, string_top, string_bottom, 3)
        
        # Draw arrow being drawn
        if self.is_drawing and self.hand_start_pos and self.draw_power > 0:
            # Arrow shaft
            arrow_end_x = bow_x - 30 - (self.draw_power * 80)
            pygame.draw.line(self.screen, (160, 82, 45), 
                           (bow_x - 10, bow_y), (arrow_end_x, bow_y), 4)
            
            # Arrow fletching
            pygame.draw.polygon(self.screen, RED, [
                (arrow_end_x - 10, bow_y - 5),
                (arrow_end_x - 20, bow_y),
                (arrow_end_x - 10, bow_y + 5)
            ])
            
            # Power indicator
            power_bar_width = int(self.draw_power * 100)
            power_bar_color = GREEN if self.draw_power < 0.7 else YELLOW if self.draw_power < 0.9 else RED
            
            pygame.draw.rect(self.screen, power_bar_color,
                           (bow_x - 50, bow_y - 80, power_bar_width, 10))
            pygame.draw.rect(self.screen, WHITE,
                           (bow_x - 50, bow_y - 80, 100, 10), 2)
    
    def draw_crosshair(self):
        """Draw aiming crosshair"""
        hand_data = self.hand_tracker.hand_data
        
        if hand_data.active and hand_data.hands_count > 0:
            x, y = hand_data.x, hand_data.y
            
            # Pulsing crosshair
            pulse_size = 5 + math.sin(self.crosshair_pulse) * 3
            crosshair_color = YELLOW if hand_data.pinching else GREEN
            
            # Draw crosshair lines
            pygame.draw.line(self.screen, crosshair_color,
                           (x - 20, y), (x + 20, y), 3)
            pygame.draw.line(self.screen, crosshair_color,
                           (x, y - 20), (x, y + 20), 3)
            
            # Center circle
            pygame.draw.circle(self.screen, crosshair_color, (x, y), int(pulse_size), 2)
    
    def draw_game(self):
        """Draw archery game elements"""
        # Draw title with Adidas styling
        title_text = self.font_title.render("ADIDAS ARCHERY", True, WHITE)
        title_x = 250
        title_y = 40
        self.screen.blit(title_text, (title_x, title_y))
        
        # Subtitle
        subtitle_text = self.font_small.render("Precision Challenge", True, RED)
        subtitle_x = title_x
        subtitle_y = title_y + 50
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # Draw targets
        for target in self.targets:
            target.draw(self.screen)
        
        # Draw bow
        self.draw_bow()
        
        # Draw arrows in flight
        for arrow in self.arrows_fired:
            arrow.draw(self.screen)
        
        # Draw crosshair
        self.draw_crosshair()
        
        # Game UI
        ui_y = 120
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (50, ui_y))
        
        # Arrows left
        arrows_text = self.font_medium.render(f"Arrows: {self.arrows_left}", True, WHITE)
        self.screen.blit(arrows_text, (50, ui_y + 40))
        
        # Timer
        if self.countdown_started:
            time_color = RED if self.game_time < 10 else WHITE
            time_text = self.font_medium.render(f"Time: {self.game_time:.1f}s", True, time_color)
            self.screen.blit(time_text, (50, ui_y + 80))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Final score
            final_score_text = self.font_title.render(f"Final Score: {self.score}", True, YELLOW)
            score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
            self.screen.blit(final_score_text, score_rect)
            
            # Performance message
            if self.score >= 200:
                message = "EXCELLENT! Professional Level!"
                message_color = GREEN
            elif self.score >= 100:
                message = "GREAT! Keep practicing!"
                message_color = YELLOW
            else:
                message = "Good try! Practice makes perfect!"
                message_color = WHITE
            
            message_text = self.font_medium.render(message, True, message_color)
            message_rect = message_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            self.screen.blit(message_text, message_rect)
        
        # Draw reset button
        self.reset_button.draw(self.screen, self.font_small)
        
        # Instructions
        instructions = [
            "PINCH and PULL BACK to draw bow | RELEASE to shoot",
            "Aim with hand position | Bullseye = 100pts",
            "R: Reset | ESC: Back to Menu"
        ]
        
        instruction_y = self.screen.get_height() - 80
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, instruction_y + i * 25))
            self.screen.blit(text, text_rect)