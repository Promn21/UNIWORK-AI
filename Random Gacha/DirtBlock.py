import random
import pygame

COLOR_CHANGE_RATE = 25
BASE_BLOCK_SIZE = 100
COOLDOWN_TIME = 0  # 1 second cooldown

class Block:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.block_color = [random.randint(139, 179), 69, 19]  # Brownish color
        self.block_size = BASE_BLOCK_SIZE
        self.block = pygame.Rect(self.screen_width // 2 - self.block_size // 2, 
                                 self.screen_height // 2 - self.block_size // 2, 
                                 self.block_size, self.block_size)
        self.last_block_break_time = 0

    def spawn_new_block(self):
        """Spawn a new block with random brown gradient color and random size."""
        self.block_color = [179, 69, 19] 
        
        # Random block size (10% - 20% bigger or smaller)
        size_modifier = random.uniform(0.8, 1.2)
        self.block_size = int(BASE_BLOCK_SIZE * size_modifier)
        
        # Recalculate the block's position and size
        self.block = pygame.Rect(self.screen_width // 2 - self.block_size // 2, 
                                 self.screen_height // 2 - self.block_size // 2, 
                                 self.block_size, self.block_size)

    def darken_block(self):
        """Darken the block color by a fixed rate."""
        self.block_color[0] = max(0, self.block_color[0] - COLOR_CHANGE_RATE)
    
    def can_break_block(self):
        """Check if the block can break (based on a cooldown timer)."""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_block_break_time >= COOLDOWN_TIME

    def update_last_break_time(self):
        """Update the block's last break time after a successful break."""
        self.last_block_break_time = pygame.time.get_ticks()
