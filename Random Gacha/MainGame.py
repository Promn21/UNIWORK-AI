import pygame
import random
from DirtBlock import Block
from Message import Message
from Utility import MarbleBagRandom, Predetermination, FixedRateProb, ProgressiveProb

# Constants
MINERAL_DROP_PROBABILITY = 30  # Fixed probability for finding minerals
FIXED_SUCCESS_RATE = 3  # Successful drop after 3 attempts
MAX_ATTEMPTS = 3  # For the predetermination
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize probability classes
fixed_rate_prob = FixedRateProb(MINERAL_DROP_PROBABILITY, FIXED_SUCCESS_RATE)
predetermination = Predetermination(MAX_ATTEMPTS)

# Mineral colors (Real-life materials)
MATERIAL_COLORS = {
    "Gold": (255, 215, 0),
    "Silver": (192, 192, 192),
    "Diamond": (185, 242, 255)
}

# Game setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Game variables
block = Block(SCREEN_WIDTH, SCREEN_HEIGHT)
mineral_bag = MarbleBagRandom(["Gold", "Silver", "Diamond"], seed=42)
fail_counter = 0
mineral_drop_prob = 0.3
break_prob = 0.5
messages = []

# Screen shake variables
shake_duration = 0  # How long the screen shake lasts
shake_intensity = 5  # How strong the shake effect is

def start_screen_shake(duration):
    """Starts a screen shake effect for a given duration."""
    global shake_duration
    shake_duration = duration

def dig_block(event):
    """Handle the action of digging the block."""
    global fail_counter
    if not block.can_break_block():
        return

    if random.random() < break_prob:
        # Get the mouse position where the click occurred
        mouse_position = event.pos
        start_screen_shake(10)
        # Display "Break!" message at the mouse position in red
        messages.append(Message("Break!", mouse_position, (255, 0, 0), SCREEN_WIDTH, SCREEN_HEIGHT))  # Red color for "break"
        
        # Check if the player should receive a guaranteed mineral on the fourth attempt
        if predetermination.attempt() or fixed_rate_prob.attempt():
            mineral = mineral_bag.draw()  # Draw a mineral from the MarbleBagRandom
            # Set realistic colors for minerals
            if mineral == "Gold":
                mineral_color = (255, 215, 0)  # Gold color
            elif mineral == "Silver":
                mineral_color = (192, 192, 192)  # Silver color
            elif mineral == "Diamond":
                mineral_color = (185, 242, 255)  # Diamond color
            
            messages.append(Message(f"Found {mineral}!", mouse_position, mineral_color, SCREEN_WIDTH, SCREEN_HEIGHT))
            fail_counter = 0  # Reset fail counter after finding a mineral
        else:
            # No mineral found
            messages.append(Message("No mineral found.", mouse_position, (0, 0, 0), SCREEN_WIDTH, SCREEN_HEIGHT))  # Black for "No mineral found."
            fail_counter += 1  # Increase fail counter when no mineral is found

        block.spawn_new_block()
        block.update_last_break_time()
    else:
        block.darken_block()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if block.block.collidepoint(event.pos):
                dig_block(event)

    # Update all messages
    for message in messages[:]:
        message.update()
        if message.is_expired():
            messages.remove(message)

    # Screen shake logic
    screen_offset = [0, 0]
    if shake_duration > 0:
        # Randomly offset the screen within the shake intensity
        screen_offset[0] = random.randint(-shake_intensity, shake_intensity)
        screen_offset[1] = random.randint(-shake_intensity, shake_intensity)
        shake_duration -= 1  # Decrease the shake duration

    # Drawing the dirt block
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, block.block_color, block.block.move(screen_offset))  # Apply screen shake offset

    # Draw all messages
    for message in messages:
        message.draw(screen, offset=screen_offset)  # Apply shake offset to messages too

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
