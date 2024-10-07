import random
import pygame

COLOR_CHANGE_RATE = 15
BASE_BLOCK_SIZE = 100

class Block:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.block_color = [179, 69, 19]  # dirt color I think
        self.block_size = BASE_BLOCK_SIZE
        self.block = pygame.Rect(self.screen_width // 2 - self.block_size // 2, 
                                 self.screen_height // 2 - self.block_size // 2, 
                                 self.block_size, self.block_size)

    def spawn_new_block(self):
        self.block_color = [179, 69, 19] 
        
        size_modifier = random.uniform(0.8, 1.2) # random block size 10% - 20% bigger or smaller 
        self.block_size = int(BASE_BLOCK_SIZE * size_modifier)
        
        self.block = pygame.Rect(self.screen_width // 2 - self.block_size // 2, 
                                 self.screen_height // 2 - self.block_size // 2, 
                                 self.block_size, self.block_size)   # recalculate position and size after random

    def darken_block(self):
        self.block_color[0] = max(0, self.block_color[0] - COLOR_CHANGE_RATE)
