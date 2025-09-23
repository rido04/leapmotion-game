# games/balloon_pop.py
"""
Balloon Pop Game using hand tracking
Pop balloons as they float up from the bottom
Fixed fullscreen layout alignment issues
"""

import pygame
import random
import math
import time
from .base_game import BaseGame
from core import *


class Balloon:
    """Individual balloon object"""
    def __init__(self, x, y, balloon_image, color_name, screen_width, screen_height):
        self.original_image = balloon_image
        self.image = balloon_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.color_name = color_name
        
        # Store screen dimensions for boundary checking
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Movement properties
        self.speed_y = random.uniform(1.0, 3.0)  # Upward speed
        self.speed_x = random.uniform(-0.5, 0.5)  # Slight horizontal drift
        self.float_amplitude = random.uniform(10, 20)  # Floating side-to-side
        self.float_frequency = random.uniform(0.5, 1.5)
        self.initial_x = x
        
        # Visual properties
        self.scale = random.uniform(0.8, 1.2)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.bob_offset = random.uniform(0, math.pi * 2)
        
        # State
        self.popped = False
        self.pop_animation = 0.0
        self.hover_scale = 1.0
        self.glow_animation = 0
        
        # Apply initial scaling
        self.apply_scale()
        
        # Score value based on speed (faster = more points)
        self.points = int(50 + (self.speed_y - 1.0) * 30)
    
    def apply_scale(self):
        """Apply current scale to the balloon image"""
        new_width = int(self.original_image.get_width() * self.scale * self.hover_scale)
        new_height = int(self.original_image.get_height() * self.scale * self.hover_scale)
        if new_width > 0 and new_height > 0:
            self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def update(self, dt, time_elapsed):
        """Update balloon position and animations"""
        if self.popped:
            self.pop_animation += dt * 5
            return self.pop_animation < 1.0  # Return False when animation is done
        
        # Update position
        self.rect.y -= self.speed_y
        
        # Floating motion
        float_offset = math.sin(time_elapsed * self.float_frequency + self.bob_offset) * self.float_amplitude
        self.rect.centerx = self.initial_x + self.speed_x * time_elapsed + float_offset
        
        # Keep balloon within screen bounds horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update hover scale animation
        target_hover = 1.0
        self.hover_scale += (target_hover - self.hover_scale) * 8 * dt
        
        # Update glow animation
        self.glow_animation += dt * 3
        
        # Apply scaling
        self.apply_scale()
        
        # Remove balloon if it goes off screen
        return self.rect.bottom > -100
    
    def set_hover(self, hovering):
        """Set hover state for visual feedback"""
        if hovering and not self.popped:
            self.hover_scale = 1.1
            self.glow_animation = 0  # Reset glow
    
    def pop(self):
        """Pop the balloon"""
        if not self.popped:
            self.popped = True
            return True
        return False
    
    def check_collision(self, x, y, radius=30):
        """Check if point is within balloon collision area"""
        if self.popped:
            return False
        
        # Use balloon center for collision
        balloon_center_x = self.rect.centerx
        balloon_center_y = self.rect.centery
        
        distance = math.sqrt((x - balloon_center_x) ** 2 + (y - balloon_center_y) ** 2)
        return distance < radius
    
    def draw(self, screen, time_elapsed):
        """Draw the balloon with effects"""
        if self.popped and self.pop_animation >= 1.0:
            return
        
        if self.popped:
            # Pop animation - balloon disappears with particles
            alpha = int(255 * (1 - self.pop_animation))
            pop_scale = 1 + self.pop_animation * 2
            
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            temp_surface.blit(self.image, (0, 0))
            temp_surface.set_alpha(alpha)
            
            # Scale for pop effect
            if pop_scale != 1:
                old_center = self.rect.center
                scaled_width = int(self.image.get_width() * pop_scale)
                scaled_height = int(self.image.get_height() * pop_scale)
                if scaled_width > 0 and scaled_height > 0:
                    temp_surface = pygame.transform.scale(temp_surface, (scaled_width, scaled_height))
                    temp_rect = temp_surface.get_rect()
                    temp_rect.center = old_center
                    screen.blit(temp_surface, temp_rect)
            else:
                screen.blit(temp_surface, self.rect)
            
            # Draw pop particles
            for i in range(5):
                particle_angle = i * (math.pi * 2 / 5) + self.pop_animation * math.pi
                particle_distance = self.pop_animation * 50
                particle_x = self.rect.centerx + math.cos(particle_angle) * particle_distance
                particle_y = self.rect.centery + math.sin(particle_angle) * particle_distance
                particle_size = max(1, int(8 * (1 - self.pop_animation)))
                particle_color = (255, 255 - int(self.pop_animation * 200), 0)
                pygame.draw.circle(screen, particle_color, (int(particle_x), int(particle_y)), particle_size)
        else:
            # Draw glow effect when hovered
            if self.hover_scale > 1.05:
                glow_radius = int(max(self.rect.width, self.rect.height) * 0.7)
                glow_alpha = int(100 * (self.hover_scale - 1) * 10)
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 255, 255, glow_alpha), (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius))
            
            # Draw shadow
            shadow_offset = 5
            shadow_alpha = 100
            shadow_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, shadow_alpha))
            shadow_rect = self.rect.copy()
            shadow_rect.move_ip(shadow_offset, shadow_offset)
            screen.blit(shadow_surface, shadow_rect)
            
            # Draw main balloon with optional rotation
            if abs(self.rotation) > 1:
                rotated_image = pygame.transform.rotate(self.image, self.rotation)
                rotated_rect = rotated_image.get_rect(center=self.rect.center)
                screen.blit(rotated_image, rotated_rect)
            else:
                screen.blit(self.image, self.rect)
        
        # Draw points preview when hovered
        if self.hover_scale > 1.05 and not self.popped:
            points_text = f"+{self.points}"
            font = pygame.font.Font(None, 24)
            points_surface = font.render(points_text, True, WHITE)
            points_rect = points_surface.get_rect(center=(self.rect.centerx, self.rect.top - 20))
            
            # Draw background for points
            bg_rect = points_rect.inflate(10, 4)
            pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect, border_radius=5)
            screen.blit(points_surface, points_rect)


class BalloonPopGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Balloon Pop - Hand Tracking")
        
        # Load balloon images
        self.balloon_images = {}
        self.balloon_colors = ['orange', 'gray', 'cyan', 'pink', 'blue', 'red']
        
        # Create balloon images from colors (placeholder until we load actual images)
        self.create_balloon_images()
        
        # Game state
        self.balloons = []
        self.score = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.max_missed = 10
        self.game_over = False
        self.level = 1
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # Seconds between spawns
        self.last_spawn_time = time.time()
        
        # Hand tracking
        self.last_pinch = False
        self.hand_trail = []  # For visual trail effect
        
        # Game progression
        self.balloons_for_next_level = 20
        
        # UI Elements - will be positioned dynamically
        self.create_game_buttons()
        
        # Particle system for effects
        self.particles = []
        
        # Initialize first spawn
        self.last_spawn_time = time.time()
    
    def create_game_buttons(self):
        """Create game-specific buttons with dynamic positioning"""
        current_width, current_height = self.get_current_screen_size()
        
        self.restart_button = AnimatedButton(
            current_width - 580, 20, 120, 50, "🎈 New Game", PURPLE, GREEN
        )
    
    def recalculate_game_layout(self):
        """Recalculate game-specific layout when screen size changes"""
        print("Recalculating Balloon Pop layout...")
        self.create_game_buttons()
        
        # Update existing balloons with new screen dimensions
        current_width, current_height = self.get_current_screen_size()
        for balloon in self.balloons:
            balloon.screen_width = current_width
            balloon.screen_height = current_height
        
    def get_game_info(self):
        return {
            'name': 'Balloon Pop',
            'description': 'Pop floating balloons with hand gestures',
            'preview_color': (255, 100, 150)
        }
    
    def create_balloon_images(self):
        """Load actual balloon images"""
        balloon_files = {
            'orange': 'assets/balloons/balon_adidas_orange.png',
            'gray': 'assets/balloons/balon_adidas_grey.png', 
            'cyan': 'assets/balloons/balon_adidas_biru_muda.png',
            'pink': 'assets/balloons/balon_adidas_pink.png',
            'blue': 'assets/balloons/balon_adidas_biru.png',
            'red': 'assets/balloons/balon_adidas_merah.png'
        }

        # Try to load actual images first
        for color_name, file_path in balloon_files.items():
            try:
                image = pygame.image.load(file_path).convert_alpha()  # Add convert_alpha()
                # Resize if needed
                image = pygame.transform.scale(image, (80, 100))
                self.balloon_images[color_name] = image
            except:
                print(f"Could not load {file_path}, using fallback")
                # Fallback to drawing simple balloons
                balloon_size = (80, 100)
                surface = pygame.Surface(balloon_size, pygame.SRCALPHA)
                
                # Color mapping
                color_map = {
                    'orange': (255, 165, 0),
                    'gray': (128, 128, 128),
                    'cyan': (0, 255, 255),
                    'pink': (255, 192, 203),
                    'blue': (0, 100, 255),
                    'red': (255, 50, 50)
                }
                
                color = color_map.get(color_name, (255, 255, 255))
                
                # Draw balloon shape
                balloon_rect = pygame.Rect(10, 5, 60, 75)
                pygame.draw.ellipse(surface, color, balloon_rect)
                
                # Add highlight
                highlight_rect = pygame.Rect(20, 15, 15, 20)
                highlight_color = tuple(min(255, c + 50) for c in color)
                pygame.draw.ellipse(surface, highlight_color, highlight_rect) 
                
                # Draw string
                string_start = (balloon_rect.centerx, balloon_rect.bottom)
                string_end = (balloon_rect.centerx + 2, balloon_size[1] - 5)
                pygame.draw.line(surface, (139, 69, 19), string_start, string_end, 2)
                
                self.balloon_images[color_name] = surface
    
    def spawn_balloon(self):
        """Spawn a new balloon"""
        current_width, current_height = self.get_current_screen_size()
        
        # Random position along bottom of screen using dynamic width
        x = random.randint(50, current_width - 50)
        y = current_height + 50  # Start below screen
        
        # Random balloon color
        color_name = random.choice(self.balloon_colors)
        balloon_image = self.balloon_images[color_name]
        
        balloon = Balloon(x, y, balloon_image, color_name, current_width, current_height)
        self.balloons.append(balloon)
    
    def handle_game_events(self, event):
        """Handle balloon pop game events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check restart button
            if self.restart_button.is_clicked(event.pos, True):
                self.restart_game()
            else:
                # Check balloon clicks (for debugging)
                for balloon in self.balloons:
                    if balloon.check_collision(event.pos[0], event.pos[1]):
                        if balloon.pop():
                            self.score += balloon.points
                            self.balloons_popped += 1
                            print(f"Balloon popped! +{balloon.points} points")
                        break
    
    def restart_game(self):
        """Restart the game"""
        self.balloons = []
        self.score = 0
        self.balloons_popped = 0
        self.balloons_missed = 0
        self.game_over = False
        self.level = 1
        self.spawn_interval = 2.0
        self.last_spawn_time = time.time()
        self.particles = []
        print("Game restarted!")
    
    def update_game(self):
        """Update balloon pop game state"""
        if self.game_over:
            return
            
        current_time = time.time()
        dt = 1/60
        
        # Spawn new balloons
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_balloon()
            self.last_spawn_time = current_time
            
            # Occasionally spawn multiple balloons
            if random.random() < 0.3:  # 30% chance
                if random.random() < 0.5:  # 50% of that for second balloon
                    self.spawn_balloon()
        
        # Update balloons
        remaining_balloons = []
        for balloon in self.balloons:
            if balloon.update(dt, self.background_manager.time_elapsed):
                remaining_balloons.append(balloon)
            else:
                # Balloon went off screen
                if not balloon.popped:
                    self.balloons_missed += 1
                    if self.balloons_missed >= self.max_missed:
                        self.game_over = True
                        print("Game Over! Too many balloons missed.")
        
        self.balloons = remaining_balloons
        
        # Hand tracking
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Use mouse if no hand tracking
        if not hand_data.active or hand_data.hands_count == 0:
            hand_data.x, hand_data.y = mouse_pos
        
        # Update hand trail
        if hand_data.active and hand_data.hands_count > 0:
            self.hand_trail.append((hand_data.x, hand_data.y, current_time))
            # Keep trail short
            self.hand_trail = [(x, y, t) for x, y, t in self.hand_trail if current_time - t < 0.5]
        
        # Check balloon hover states
        hovered_balloon = None
        for balloon in self.balloons:
            hovering = balloon.check_collision(hand_data.x, hand_data.y, 40)
            balloon.set_hover(hovering)
            if hovering:
                hovered_balloon = balloon
        
        # Handle pinch gesture
        if hand_data.pinching and not self.last_pinch and hovered_balloon:
            if hovered_balloon.pop():
                self.score += hovered_balloon.points
                self.balloons_popped += 1
                
                # Create celebration particles
                for _ in range(8):
                    self.particles.append({
                        'x': hovered_balloon.rect.centerx,
                        'y': hovered_balloon.rect.centery,
                        'vx': random.uniform(-100, 100),
                        'vy': random.uniform(-150, -50),
                        'life': 1.0,
                        'color': (255, 255, 0)
                    })
                
                print(f"Pinch pop! +{hovered_balloon.points} points. Score: {self.score}")
        
        self.last_pinch = hand_data.pinching
        
        # Update particles
        remaining_particles = []
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] += 300 * dt  # Gravity
            particle['life'] -= dt * 2
            
            if particle['life'] > 0:
                remaining_particles.append(particle)
        
        self.particles = remaining_particles
        
        # Level progression
        if self.balloons_popped >= self.balloons_for_next_level:
            self.level += 1
            self.balloons_for_next_level += 15
            self.spawn_interval = max(0.5, self.spawn_interval - 0.1)  # Faster spawning
            print(f"Level up! Now level {self.level}")
        
        # Update UI
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        self.restart_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        if self.restart_button.is_hand_activated():
            self.restart_game()
    
    def draw_game(self):
        """Draw balloon pop game"""
        current_width, current_height = self.get_current_screen_size()
        
        # Draw title
        title_text = self.font_title.render("BALLOON POP", True, WHITE)
        title_x = 250
        title_y = 40
        self.screen.blit(title_text, (title_x, title_y))
        
        # Draw subtitle
        subtitle = "Pop floating balloons with pinch gestures"
        subtitle_text = self.font_small.render(subtitle, True, (255, 100, 150))
        self.screen.blit(subtitle_text, (title_x, title_y + 50))
        
        # Draw balloons
        for balloon in self.balloons:
            balloon.draw(self.screen, self.background_manager.time_elapsed)
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            size = max(1, int(5 * particle['life']))
            color = (*particle['color'], alpha)
            
            # Create surface for alpha blending
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            self.screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        # Draw hand trail
        if len(self.hand_trail) > 1:
            for i in range(1, len(self.hand_trail)):
                start_pos = self.hand_trail[i-1][:2]
                end_pos = self.hand_trail[i][:2]
                alpha = int(255 * (i / len(self.hand_trail)))
                
                # Create surface for alpha line - Fixed: use dynamic screen size
                if alpha > 0:
                    trail_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
                    pygame.draw.line(trail_surface, (0, 255, 255, alpha), start_pos, end_pos, max(1, 5 - i))
                    self.screen.blit(trail_surface, (0, 0))
        
        # Draw hand indicator
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            pulse = math.sin(self.background_manager.time_elapsed * 8) * 2 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            
            # Draw pinch indicator
            if hand_data.pinching:
                pygame.draw.circle(self.screen, YELLOW, (hand_data.x, hand_data.y), int(pulse + 5), 3)
            
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
        
        # Draw game stats
        stats_x = 50
        stats_y = 150
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (stats_x, stats_y))
        
        # Level
        level_text = self.font_medium.render(f"Level: {self.level}", True, CYAN)
        self.screen.blit(level_text, (stats_x, stats_y + 35))
        
        # Balloons popped
        popped_text = self.font_medium.render(f"Popped: {self.balloons_popped}", True, GREEN)
        self.screen.blit(popped_text, (stats_x, stats_y + 70))
        
        # Balloons missed
        missed_color = RED if self.balloons_missed > self.max_missed // 2 else WHITE
        missed_text = self.font_medium.render(f"Missed: {self.balloons_missed}/{self.max_missed}", True, missed_color)
        self.screen.blit(missed_text, (stats_x, stats_y + 105))
        
        # Progress to next level
        progress = self.balloons_popped % (self.balloons_for_next_level - (self.level - 1) * 15)
        needed = self.balloons_for_next_level - (self.level - 1) * 15 - progress
        progress_text = self.font_small.render(f"Next level: {needed} more", True, LIGHT_GRAY)
        self.screen.blit(progress_text, (stats_x, stats_y + 140))
        
        # Game status - Fixed: use dynamic screen size
        center_x = current_width // 2
        status_y = current_height - 120
        
        if self.game_over:
            game_over_text = self.font_large.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(center_x, status_y - 40))
            self.screen.blit(game_over_text, game_over_rect)
            
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(center_x, status_y))
            self.screen.blit(final_score_text, final_score_rect)
        else:
            if hand_data.active and hand_data.hands_count > 0:
                status = f"Hand Tracking Active - {len(self.balloons)} balloons"
                status_color = GREEN
            else:
                status = "Using mouse (no hand tracking detected)"
                status_color = LIGHT_GRAY
            
            status_text = self.font_medium.render(status, True, status_color)
            status_rect = status_text.get_rect(center=(center_x, status_y))
            self.screen.blit(status_text, status_rect)
        
        # Draw restart button
        self.restart_button.draw(self.screen, self.font_small)
        
        # Instructions - Fixed: use dynamic screen size
        instructions = [
            "Use PINCH gesture to pop balloons",
            "Don't let too many escape!",
            "Mouse click also works | R: Restart | ESC: Menu"
        ]
        instruction_y = current_height - 80
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(center_x, instruction_y + i * 20))
            self.screen.blit(text, text_rect)