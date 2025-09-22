# games/stack_tower.py
"""
Hand Stack Tower Game
Stack blocks to build the tallest tower using hand tracking
"""

import pygame
import random
import math
import time
from .base_game import BaseGame
from core import *


class Block:
    """Individual tower block"""
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel_y = 0
        self.vel_x = 0
        self.is_falling = True
        self.is_placed = False
        self.wobble = 0
        self.wobble_speed = 0
        self.stability = 1.0
        self.placed_time = 0
        
        # Visual effects
        self.glow_intensity = 0
        self.pulse_phase = random.random() * math.pi * 2
        
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def center_x(self):
        return self.x + self.width / 2
    
    @property
    def bottom(self):
        return self.y + self.height
        
    def update(self, dt, gravity=500):
        """Update block physics"""
        if self.is_falling:
            self.vel_y += gravity * dt
            self.y += self.vel_y * dt
            self.x += self.vel_x * dt
            
            # Add slight air resistance
            self.vel_x *= 0.999
        
        elif self.is_placed:
            # Wobble physics for placed blocks
            self.wobble_speed += -self.wobble * 8 * dt - self.wobble_speed * 4 * dt
            self.wobble += self.wobble_speed * dt
            
            # Damping
            self.wobble *= 0.995
            self.wobble_speed *= 0.99
            
            # Update stability based on wobble
            wobble_factor = abs(self.wobble)
            self.stability = max(0.1, 1.0 - wobble_factor * 0.1)
            
        # Visual effects
        if self.is_falling:
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 3)
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - dt * 2)
            
    def stop_falling(self, ground_y):
        """Stop the block from falling"""
        self.is_falling = False
        self.is_placed = True
        self.y = ground_y - self.height
        self.vel_y = 0
        self.vel_x *= 0.3  # Reduce horizontal momentum
        self.placed_time = time.time()
        
        # Add some wobble based on impact
        impact_wobble = abs(self.vel_y) * 0.001 + abs(self.vel_x) * 0.005
        self.wobble = random.uniform(-impact_wobble, impact_wobble)
        
    def apply_influence(self, neighbor_wobble):
        """Apply influence from neighboring blocks"""
        if self.is_placed:
            influence_strength = 0.1
            self.wobble += neighbor_wobble * influence_strength
            
    def check_collision(self, other):
        """Check if this block collides with another"""
        return self.rect.colliderect(other.rect)
        
    def get_overlap_amount(self, other):
        """Get how much this block overlaps with another (for stability calculation)"""
        if not self.check_collision(other):
            return 0
            
        left = max(self.x, other.x)
        right = min(self.x + self.width, other.x + other.width)
        overlap_width = right - left
        
        return overlap_width / min(self.width, other.width)
        
    def draw(self, screen, time_elapsed, camera_offset_y=0):
        """Draw the block with effects"""
        draw_y = self.y + camera_offset_y
        draw_x = self.x + self.wobble * 20  # Visual wobble effect
        
        # Skip if off screen
        if draw_y > WINDOW_HEIGHT + 100 or draw_y < -200:
            return
            
        block_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        
        # Glow effect for falling blocks
        if self.glow_intensity > 0:
            glow_size = int(self.glow_intensity * 10)
            glow_surface = pygame.Surface((self.width + glow_size * 2, self.height + glow_size * 2))
            glow_surface.set_alpha(int(self.glow_intensity * 100))
            pygame.draw.rect(glow_surface, self.color, 
                           (0, 0, self.width + glow_size * 2, self.height + glow_size * 2),
                           border_radius=5)
            screen.blit(glow_surface, (draw_x - glow_size, draw_y - glow_size))
        
        # Main block with stability-based transparency
        alpha = int(255 * self.stability) if self.is_placed else 255
        block_surface = pygame.Surface((self.width, self.height))
        block_surface.set_alpha(alpha)
        pygame.draw.rect(block_surface, self.color, (0, 0, self.width, self.height), border_radius=3)
        screen.blit(block_surface, (draw_x, draw_y))
        
        # Border
        border_color = WHITE if self.stability > 0.7 else YELLOW if self.stability > 0.4 else RED
        pygame.draw.rect(screen, border_color, block_rect, 2, border_radius=3)
        
        # Stability indicator for placed blocks
        if self.is_placed and self.stability < 0.9:
            stability_width = int(self.width * self.stability)
            stability_rect = pygame.Rect(draw_x, draw_y - 5, stability_width, 3)
            stability_color = GREEN if self.stability > 0.7 else YELLOW if self.stability > 0.4 else RED
            pygame.draw.rect(screen, stability_color, stability_rect)


class StackTowerGame(BaseGame):
    def __init__(self, screen=None):
        super().__init__(screen)
        pygame.display.set_caption("Stack Tower - Hand Tracking")
        
        # Game settings
        self.ground_level = WINDOW_HEIGHT - 100
        self.spawn_height = -50
        self.block_base_width = 120
        self.block_height = 30
        self.block_min_width = 40
        
        # Game state
        self.blocks = []
        self.current_block = None
        self.tower_height = 0
        self.level = 1
        self.score = 0
        self.game_over = False
        self.game_won = False
        
        # Visual state
        self.camera_offset_y = 0
        self.target_camera_y = 0
        self.shake_intensity = 0
        
        # Hand tracking
        self.last_pinch = False
        self.pinch_start_time = 0
        self.drop_delay = 0.3  # seconds to hold pinch before drop
        
        # Timing
        self.spawn_timer = 0
        self.spawn_delay = 2.0
        self.level_up_timer = 0
        
        # Colors for blocks
        self.block_colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green  
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
            (255, 150, 100),  # Orange
            (150, 100, 255),  # Purple
        ]
        
        # UI
        self.new_game_button = AnimatedButton(
            WINDOW_WIDTH - 580, 20, 120, 50, "New Game", GREEN_DARK, GREEN
        )
        
        # Initialize game
        self.setup_game()
    
    def get_game_info(self):
        return {
            'name': 'Stack Tower',
            'description': 'Stack blocks to build the tallest tower',
            'preview_color': (255, 165, 0)  # Orange
        }
        
    def setup_game(self):
        """Initialize a new game"""
        self.blocks = []
        self.current_block = None
        self.tower_height = 0
        self.level = 1
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.camera_offset_y = 0
        self.target_camera_y = 0
        self.shake_intensity = 0
        self.spawn_timer = 0
        self.level_up_timer = 0
        
        # Add ground block
        ground_block = Block(
            WINDOW_WIDTH // 2 - self.block_base_width // 2,
            self.ground_level - self.block_height,
            self.block_base_width,
            self.block_height,
            DARK_GRAY
        )
        ground_block.is_falling = False
        ground_block.is_placed = True
        ground_block.stability = 1.0
        self.blocks.append(ground_block)
        
    def spawn_new_block(self):
        """Spawn a new block at the top"""
        if self.current_block is None or self.current_block.is_placed:
            # Calculate new block width (gets smaller each level)
            width_reduction = (self.level - 1) * 8
            block_width = max(self.block_min_width, self.block_base_width - width_reduction)
            
            # Random spawn position
            spawn_x = random.randint(50, WINDOW_WIDTH - block_width - 50)
            
            # Choose color
            color = self.block_colors[self.level % len(self.block_colors)]
            
            self.current_block = Block(
                spawn_x,
                self.spawn_height,
                block_width,
                self.block_height,
                color
            )
            
            # Add some initial horizontal velocity for challenge
            max_vel = 100 + self.level * 20
            self.current_block.vel_x = random.uniform(-max_vel, max_vel)
            
            print(f"Spawned level {self.level} block (width: {block_width})")
            
    def check_block_placement(self, block):
        """Check if a falling block should be placed"""
        if not block.is_falling:
            return
            
        # Check collision with placed blocks
        for other in self.blocks:
            if other != block and other.is_placed and block.check_collision(other):
                # Place the block on top of the collision
                ground_y = other.y
                block.stop_falling(ground_y)
                
                # Calculate stability based on overlap
                overlap = block.get_overlap_amount(other)
                block.stability = min(1.0, overlap * 1.2)  # Bonus for good placement
                
                # Update tower height
                self.tower_height = max(self.tower_height, len([b for b in self.blocks if b.is_placed]))
                
                # Add to blocks list if it's the current block
                if block == self.current_block:
                    self.blocks.append(block)
                    self.score += int(100 * block.stability * self.level)
                    self.level += 1
                    
                    # Screen shake on placement
                    self.shake_intensity = 5
                    
                    # Check win condition (tower of 15 blocks)
                    if self.tower_height >= 15:
                        self.game_won = True
                        self.game_over = True
                        print("You won! Tower completed!")
                        
                return
                
        # Check ground collision
        if block.bottom >= self.ground_level:
            if len(self.blocks) == 1:  # Only ground block exists
                block.stop_falling(self.ground_level)
                if block == self.current_block:
                    self.blocks.append(block)
                    self.score += int(100 * block.stability * self.level)
                    self.level += 1
                    self.shake_intensity = 3
            else:
                # Block hit ground - game over
                if block == self.current_block:
                    self.game_over = True
                    print("Game Over! Block hit the ground!")
                    
    def check_tower_stability(self):
        """Check if the tower is still stable"""
        if len(self.blocks) <= 1:
            return
            
        # Propagate wobble influence through tower
        for i in range(1, len(self.blocks)):
            current = self.blocks[i]
            if i > 1:
                below = self.blocks[i-1]
                current.apply_influence(below.wobble)
                
        # Check for catastrophic instability
        for block in self.blocks[1:]:  # Skip ground block
            if block.is_placed and block.stability < 0.1:
                self.game_over = True
                print("Game Over! Tower collapsed!")
                return
                
    def update_camera(self):
        """Update camera to follow the tower"""
        if len(self.blocks) > 3:
            # Find the highest block
            highest_y = min(block.y for block in self.blocks if block.is_placed)
            self.target_camera_y = max(0, (self.ground_level - highest_y) - 200)
            
        # Smooth camera movement
        self.camera_offset_y += (self.target_camera_y - self.camera_offset_y) * 0.05
        
        # Screen shake
        if self.shake_intensity > 0:
            self.camera_offset_y += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= 0.9
            if self.shake_intensity < 0.1:
                self.shake_intensity = 0
                
    def handle_game_events(self, event):
        """Handle stack tower specific events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                self.setup_game()
            elif event.key == pygame.K_SPACE:
                if self.current_block and self.current_block.is_falling:
                    # Drop current block
                    self.current_block.vel_x = 0  # Stop horizontal movement
                    print("Block dropped with spacebar!")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check new game button
            if self.new_game_button.is_clicked(event.pos, True):
                self.setup_game()
            elif self.current_block and self.current_block.is_falling:
                # Drop current block
                self.current_block.vel_x = 0
                print("Block dropped with mouse!")
                
    def update_game(self):
        """Update stack tower game state"""
        if self.game_over:
            return
            
        dt = 1/60  # Assuming 60 FPS
        
        # Update spawn timer
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay and (self.current_block is None or self.current_block.is_placed):
            self.spawn_new_block()
            self.spawn_timer = 0
            
        # Update all blocks
        for block in self.blocks:
            block.update(dt)
            
        # Update current falling block
        if self.current_block:
            self.current_block.update(dt)
            self.check_block_placement(self.current_block)
            
        # Check tower stability
        self.check_tower_stability()
        
        # Hand tracking
        hand_data = self.hand_tracker.hand_data
        mouse_pos = pygame.mouse.get_pos()
        
        # Control current block with hand position
        if self.current_block and self.current_block.is_falling and hand_data.active and hand_data.hands_count > 0:
            # Move block towards hand X position
            target_x = hand_data.x - self.current_block.width // 2
            current_center_x = self.current_block.x + self.current_block.width // 2
            hand_center_x = hand_data.x
            
            # Apply gentle force towards hand position
            force = (hand_center_x - current_center_x) * 0.3
            self.current_block.vel_x = force
            
        # Handle pinch gesture for dropping
        if hand_data.pinching and not self.last_pinch:
            self.pinch_start_time = time.time()
            
        if hand_data.pinching and self.last_pinch:
            # Check if pinch held long enough
            if time.time() - self.pinch_start_time >= self.drop_delay:
                if self.current_block and self.current_block.is_falling:
                    self.current_block.vel_x = 0
                    print("Block dropped with pinch gesture!")
                    
        self.last_pinch = hand_data.pinching
        
        # Update camera
        self.update_camera()
        
        # Update UI buttons
        hand_pos = (hand_data.x, hand_data.y) if (hand_data.active and hand_data.hands_count > 0) else None
        self.new_game_button.update(mouse_pos, hand_pos, hand_data.pinching)
        
        # Check for hand-activated new game
        if self.new_game_button.is_hand_activated():
            self.setup_game()
            print("New game started by hand gesture!")
            
    def draw_game(self):
        """Draw stack tower specific elements"""
        current_time = time.time()
        
        # Draw title
        title_text = self.font_title.render("STACK TOWER", True, WHITE)
        title_x = 250  # After logos
        title_y = 40
        self.screen.blit(title_text, (title_x, title_y))
        
        # Draw subtitle
        subtitle_text = self.font_small.render("Build the tallest tower possible", True, (255, 165, 0))
        subtitle_x = title_x
        subtitle_y = title_y + 50
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # Draw ground line
        ground_y = self.ground_level + self.camera_offset_y
        if -50 <= ground_y <= WINDOW_HEIGHT + 50:
            pygame.draw.line(self.screen, WHITE, (0, ground_y), (WINDOW_WIDTH, ground_y), 3)
            
        # Draw all blocks
        for block in self.blocks:
            block.draw(self.screen, current_time, self.camera_offset_y)
            
        # Draw current falling block
        if self.current_block:
            self.current_block.draw(self.screen, current_time, self.camera_offset_y)
            
        # Draw hand indicator and control guide
        hand_data = self.hand_tracker.hand_data
        if hand_data.active and hand_data.hands_count > 0:
            # Hand cursor
            pulse = math.sin(self.background_manager.time_elapsed * 6) * 3 + 8
            hand_color = GREEN if not hand_data.pinching else YELLOW
            pygame.draw.circle(self.screen, hand_color, (hand_data.x, hand_data.y), int(pulse))
            pygame.draw.circle(self.screen, WHITE, (hand_data.x, hand_data.y), int(pulse), 2)
            
            # Pinch hold indicator
            if hand_data.pinching and self.current_block and self.current_block.is_falling:
                hold_time = time.time() - self.pinch_start_time
                if hold_time < self.drop_delay:
                    progress = hold_time / self.drop_delay
                    progress_width = int(100 * progress)
                    progress_rect = pygame.Rect(hand_data.x - 50, hand_data.y - 30, progress_width, 8)
                    pygame.draw.rect(self.screen, YELLOW, progress_rect, border_radius=4)
                    
                    # Progress text
                    progress_text = self.font_small.render("Hold to Drop...", True, YELLOW)
                    progress_text_rect = progress_text.get_rect(center=(hand_data.x, hand_data.y - 45))
                    self.screen.blit(progress_text, progress_text_rect)
        
        # Game stats panel
        stats_x = 20
        stats_y = 150
        
        # Background for stats
        stats_bg = pygame.Rect(stats_x - 10, stats_y - 10, 200, 150)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), stats_bg, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, stats_bg, 2, border_radius=10)
        
        # Stats text
        stats = [
            f"Level: {self.level}",
            f"Score: {self.score}",
            f"Height: {self.tower_height}",
            f"Blocks: {len(self.blocks) - 1}"  # Exclude ground
        ]
        
        for i, stat in enumerate(stats):
            text = self.font_medium.render(stat, True, WHITE)
            self.screen.blit(text, (stats_x, stats_y + i * 30))
        
        # Game status
        center_x = WINDOW_WIDTH // 2
        status_y = WINDOW_HEIGHT - 150
        
        if self.game_won:
            status = "CONGRATULATIONS! TOWER COMPLETED!"
            status_color = GREEN
        elif self.game_over:
            status = "GAME OVER! Press N for new game"
            status_color = RED
        else:
            if hand_data.active and hand_data.hands_count > 0:
                status = f"Hand Tracking: Move hand to control block"
                status_color = GREEN
            else:
                status = "Mouse mode - Click to drop block"
                status_color = LIGHT_GRAY
                
        status_text = self.font_medium.render(status, True, status_color)
        status_rect = status_text.get_rect(center=(center_x, status_y))
        self.screen.blit(status_text, status_rect)
        
        # Draw new game button
        self.new_game_button.draw(self.screen, self.font_small)
        
        # Instructions
        instructions = [
            "Move your hand left/right to control falling blocks",
            "Hold PINCH for 0.3 seconds to drop | SPACE or Click also works",
            "Stack blocks carefully - stability matters! | N: New Game | ESC: Menu"
        ]
        instruction_y = self.screen.get_height() - 80
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(center_x, instruction_y + i * 25))
            self.screen.blit(text, text_rect)