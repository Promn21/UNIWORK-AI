import pygame
import random
import enum
import math

WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 1
FOOD_SIZE = 3
MAX_SPEED = 2
HUNGER_DECAY_RATE = 5  # Hunger decreases by 5 every second
CHASE_DISTANCE = 150  # Max distance to chase the food

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("State Machine")

# Load and slice sprite sheets
def load_sprite_sheet(path, frame_count, frame_width, frame_height=64):
    sheet = pygame.image.load(path).convert_alpha()
    return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(frame_count)]

# Define animations based on corrected frame dimensions
raptor_walk_anim = load_sprite_sheet('assets/raptor-walk.png', 6, 128)
raptor_run_anim = load_sprite_sheet('assets/raptor-run.png', 6, 128)
raptor_idle_anim = load_sprite_sheet('assets/raptor-scanning.png', 18, 128)
raptor_atk_anim = load_sprite_sheet('assets/raptor-bite.png', 10, 128)
raptor_dead_anim = load_sprite_sheet('assets/raptor-dead.png', 6, 128)

# Animation frame rate
FRAME_RATE = 30

# States
class AgentState(enum.Enum):
    PATROL_STATE = 0
    CHASE_STATE = 1
    ATK_STATE = 2
    IDLE_STATE = 3
    DEAD_STATE = 4

class Agent:
    def __init__(self):
        self.hungriness = 100
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(0, 0)  # Initial velocity
        self.frame_index = 0
        self.current_state = AgentState.PATROL_STATE
        self.current_anim = raptor_walk_anim
        self.time_since_last_frame = 0
        self.anim_completed = False  # Tracks if an animation has finished

        # Patrol attributes
        self.patrol_timer = 0  # Time for patrol state
        self.patrol_duration = random.uniform(0.5, 1)  # Duration to patrol for
        self.set_random_patrol_direction()  # Set initial patrol direction

    def set_random_patrol_direction(self):
        angle = random.uniform(0, 360)  
        radians = math.radians(angle)  
        self.velocity = pygame.Vector2(MAX_SPEED * math.cos(radians), MAX_SPEED * math.sin(radians))

    def update_animation(self, dt):
        # Only update animation if not completed (for states like IDLE_STATE)
        if not self.anim_completed:
            self.frame_index += FRAME_RATE * dt
            if self.frame_index >= len(self.current_anim):
                self.frame_index = 0
                if self.current_state == AgentState.IDLE_STATE:
                    self.anim_completed = True  # Mark animation completed for idle state

    def change_state(self, new_state, new_anim):
        if self.current_state != new_state:
            self.current_state = new_state
            self.current_anim = new_anim
            self.frame_index = 0
            self.anim_completed = False  # Reset completion status for new state

            # Reset patrol if transitioning from patrol to another state
            if new_state != AgentState.PATROL_STATE:
                self.patrol_timer = 0  # Reset the patrol timer

    def update(self, target, dt):
        if self.hungriness <= 0:
            self.change_state(AgentState.DEAD_STATE, raptor_dead_anim)

        if self.current_state != AgentState.DEAD_STATE:
            self.hungriness -= HUNGER_DECAY_RATE * dt

        if self.current_state == AgentState.PATROL_STATE:
            # Update the patrol timer
            self.patrol_timer += dt
            if self.patrol_timer >= self.patrol_duration:
                self.change_state(AgentState.IDLE_STATE, raptor_idle_anim)
            else:
                # Move in the current random direction
                self.position += self.velocity
            
            # Check for nearby target to switch to CHASE_STATE
            if (target - self.position).length() < 100:
                self.change_state(AgentState.CHASE_STATE, raptor_run_anim)

        elif self.current_state == AgentState.IDLE_STATE:
            if self.anim_completed:
                self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)
                self.set_random_patrol_direction()  # Set a new patrol direction when resuming patrol

        elif self.current_state == AgentState.CHASE_STATE:
            distance_to_target = (target - self.position).length()

            # If food is too far away, return to PATROL_STATE
            if distance_to_target > CHASE_DISTANCE:
                self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)
                return  # Exit early to avoid chasing

            self.velocity = (target - self.position).normalize() * MAX_SPEED
            self.position += self.velocity
            if distance_to_target < 10:
                self.change_state(AgentState.ATK_STATE, raptor_atk_anim)

        elif self.current_state == AgentState.ATK_STATE:
            if self.frame_index >= len(self.current_anim) - 1:  # Finish attack animation
                self.hungriness = 100
                self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)

        elif self.current_state == AgentState.DEAD_STATE:
            if self.frame_index < len(self.current_anim) - 1:
                self.update_animation(dt)  # Continue playing death animation
            else:
                self.frame_index = len(raptor_dead_anim) - 1  # Set to last frame to lay down still

        self.update_animation(dt)

        # Warp around
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH
        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

    def draw(self, screen):
        # Get the current frame from the animation
        current_frame = self.current_anim[int(self.frame_index)]
        
        # Correct alignment by centering on the position
        sprite_rect = current_frame.get_rect(center=(self.position.x, self.position.y))
        
        # Flip the sprite if it's moving left
        if self.velocity.x < 0:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        # Draw the sprite centered at the position
        screen.blit(current_frame, sprite_rect)

def main():
    agents = [Agent() for _ in range(NUM_AGENTS)]
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        screen.fill((100, 100, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        target = pygame.Vector2(pygame.mouse.get_pos())

        for agent in agents:
            agent.update(target, dt)
            agent.draw(screen)

        pygame.draw.circle(screen, (255, 0, 0), (int(target.x), int(target.y)), FOOD_SIZE)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
