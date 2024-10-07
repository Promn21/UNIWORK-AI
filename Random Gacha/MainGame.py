import pygame
import random
from DirtBlock import Block
from Message import Message
from Utility import MarbleBagRandom, FixedRateProb, ProgressiveProb

##### constants #####
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# initialize probability classes
random_seed = 42  
mineral_drop_prob = 30
mineral_drop_increment = 2.5
mineral_drop_prob = ProgressiveProb(mineral_drop_prob, mineral_drop_increment) 

break_prob = 50
break_prob_increment = -2.5
progressive_break_prob = ProgressiveProb(break_prob, break_prob_increment) 

guaranteed_mineral_prob = FixedRateProb(0, 4) 

# mineral colors (real-life materials color? idk lol)
MATERIAL_COLORS = {
    "Gold": (255, 215, 0),
    "Silver": (192, 192, 192),
    "Diamond": (185, 242, 255)
}

##### Game setup #####
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

##### Game variables #####
block = Block(SCREEN_WIDTH, SCREEN_HEIGHT)
mineral_bag = MarbleBagRandom(["Gold", "Silver", "Diamond"], random_seed)
messages = []

##### SCREEN SHAKE for gamee juiciness #####
shake_duration = 0  # how long the screen shake lasts // not very long
shake_intensity = 5  # how strong the shake effect is // is kinda strong

def start_screen_shake(duration): 
    global shake_duration
    shake_duration = duration

def dig_block(event):

    if guaranteed_mineral_prob.attempt():   # check for guaranteed mineral drop on the fourth attempt
        mouse_position = event.pos
        mineral = mineral_bag.draw()  # guaranteed mineral on fourth attempt
        mineral_color = MATERIAL_COLORS[mineral]
        messages.append(Message(f"Guaranteed find: {mineral}!", mouse_position, mineral_color, SCREEN_WIDTH, SCREEN_HEIGHT))
        return  
    
    if progressive_break_prob.attempt():  # check if the block breaks
        mouse_position = event.pos
        start_screen_shake(10)
        messages.append(Message("Break!", mouse_position, (255, 0, 0), SCREEN_WIDTH, SCREEN_HEIGHT))

        guaranteed_mineral_prob.attempt_count = 0    # reset the guaranteed mineral attempts on block break

        if mineral_drop_prob.attempt():  # regular mineral finding logic using FixedRateProb
            mineral = mineral_bag.draw()
            mineral_color = MATERIAL_COLORS[mineral]
            messages.append(Message(f"Found {mineral}!", mouse_position, mineral_color, SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            messages.append(Message("No mineral found :(", mouse_position, (0, 0, 0), SCREEN_WIDTH, SCREEN_HEIGHT))

        block.spawn_new_block()
    else:
        block.darken_block()

############# Main game loop #############
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if block.block.collidepoint(event.pos):
                dig_block(event)

    #### Update all messages ####
    for message in messages[:]:
        message.update()
        if message.is_expired():
            messages.remove(message)

    #### Screen shake logic ####
    screen_offset = [0, 0]
    if shake_duration > 0:
        screen_offset[0] = random.randint(-shake_intensity, shake_intensity)
        screen_offset[1] = random.randint(-shake_intensity, shake_intensity)
        shake_duration -= 1  # decrease the shake duration

    #### drawing the dirt block ####
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, block.block_color, block.block.move(screen_offset))  # Apply screen shake offset

    #### draw all silly messages ####
    for message in messages:
        message.draw(screen, offset=screen_offset)  # shake offset for messages too


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
