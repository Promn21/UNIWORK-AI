import pygame
import random
import enum
import math

WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 50
FOOD_SIZE = 15  
MAX_PATROL_SPEED = 1.5
CHASE_SPEED = 3
HUNGER_DECAY_RATE = 15
CHASE_DISTANCE = 200

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raptor State Machine")

def load_sprite_sheet(path, frame_count, frame_width, frame_height=64):
    sheet = pygame.image.load(path).convert_alpha()
    return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(frame_count)]

raptor_walk_anim = load_sprite_sheet('assets/raptor-walk.png', 6, 128)
raptor_run_anim = load_sprite_sheet('assets/raptor-run.png', 6, 128)
raptor_idle_anim = load_sprite_sheet('assets/raptor-scanning.png', 18, 128)
raptor_atk_anim = load_sprite_sheet('assets/raptor-bite.png', 10, 128)
raptor_dead_anim = load_sprite_sheet('assets/raptor-dead.png', 6, 128)

FRAME_RATE = 30
FONT = pygame.font.Font(None, 18)  
class AgentState(enum.Enum):
    PATROL_STATE = 0
    CHASE_STATE = 1
    ATK_STATE = 2
    IDLE_STATE = 3
    DEAD_STATE = 4

class Agent:
    def __init__(self):
        self.hungriness = random.uniform(50, 100)  
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(0, 0)
        self.frame_index = 0
        self.current_state = AgentState.PATROL_STATE
        self.current_anim = raptor_walk_anim
        self.time_since_last_frame = 0
        self.anim_completed = False  
        self.target_food = None  
        self.target_agent = None  

        #patrol attributes
        self.patrol_timer = 0  
        self.patrol_duration = random.uniform(1.0, 2.0)  
        self.set_random_patrol_direction()

    def set_random_patrol_direction(self):
        angle = random.uniform(0, 360)
        radians = math.radians(angle)
        self.velocity = pygame.Vector2(MAX_PATROL_SPEED * math.cos(radians), MAX_PATROL_SPEED * math.sin(radians))

    def update_animation(self, dt):
        if not self.anim_completed:
            self.frame_index += FRAME_RATE * dt
            if self.frame_index >= len(self.current_anim):
                self.frame_index = 0
                if self.current_state == AgentState.IDLE_STATE:
                    self.anim_completed = True  

    def change_state(self, new_state, new_anim):
        if self.current_state != new_state:
            self.current_state = new_state
            self.current_anim = new_anim
            self.frame_index = 0
            self.anim_completed = False

            if new_state != AgentState.PATROL_STATE:
                self.patrol_timer = 0

    def update(self, food_list, agents, dt, agents_to_remove, blood_pools):
        if self.hungriness <= 0:
            self.change_state(AgentState.DEAD_STATE, raptor_dead_anim)

        if self.current_state != AgentState.DEAD_STATE:
            self.hungriness -= HUNGER_DECAY_RATE * dt

        if self.current_state == AgentState.PATROL_STATE:
            self.patrol_timer += dt
            if self.patrol_timer >= self.patrol_duration:
                self.change_state(AgentState.IDLE_STATE, raptor_idle_anim)
            else:
                self.position += self.velocity
            
            #change to CHASE_STATE if food is close
            for food in food_list:
                if (food - self.position).length() < CHASE_DISTANCE:
                    self.target_food = food
                    self.change_state(AgentState.CHASE_STATE, raptor_run_anim)
                    break
            
            #check for dead agents to chase
            for agent in agents:
                if agent.current_state == AgentState.DEAD_STATE and (agent.position - self.position).length() < CHASE_DISTANCE:
                    self.target_agent = agent
                    self.change_state(AgentState.CHASE_STATE, raptor_run_anim)
                    break

        elif self.current_state == AgentState.IDLE_STATE:
            if self.anim_completed:
                self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)
                self.set_random_patrol_direction()

        elif self.current_state == AgentState.CHASE_STATE:
            if self.target_food:
                distance_to_target = (self.target_food - self.position).length()
                if distance_to_target > CHASE_DISTANCE:
                    self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)
                    self.target_food = None
                    return

                self.velocity = (self.target_food - self.position).normalize() * CHASE_SPEED
                self.position += self.velocity
                if distance_to_target < FOOD_SIZE:  
                    self.change_state(AgentState.ATK_STATE, raptor_atk_anim)

            elif self.target_agent:
                distance_to_target = (self.target_agent.position - self.position).length()
                if distance_to_target > CHASE_DISTANCE:
                    self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)
                    self.target_agent = None
                    return

                self.velocity = (self.target_agent.position - self.position).normalize() * CHASE_SPEED
                self.position += self.velocity
                if distance_to_target < FOOD_SIZE:  
                    self.change_state(AgentState.ATK_STATE, raptor_atk_anim)

        elif self.current_state == AgentState.ATK_STATE:
            if self.frame_index >= len(self.current_anim) - 1:
                if self.target_food in food_list:  
                    food_list.remove(self.target_food)  # remove the food from the list
                elif self.target_agent and self.target_agent.current_state == AgentState.DEAD_STATE:
                    # Confirm dead state for the target agent
                    agents_to_remove.append(self.target_agent)  # remove target
                    blood_pools.append(self.target_agent.position)  # then add blood pool at the agent's position
                self.hungriness = 100  # reset hunger after attacking
                self.target_food = None  
                self.target_agent = None  
                self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)

        elif self.current_state == AgentState.DEAD_STATE:
            if self.frame_index < len(self.current_anim) - 1:
                self.update_animation(dt)
            else:
                self.frame_index = len(raptor_dead_anim) - 1  

        self.update_animation(dt)
        self.wrap_around_screen()

    def wrap_around_screen(self):
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH
        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

    def render_hunger(self, screen):
        hunger_text = FONT.render(f"Hunger: {int(self.hungriness)}", True, (255, 255, 255))
        text_rect = hunger_text.get_rect(center=(self.position.x, self.position.y - 40))
        screen.blit(hunger_text, text_rect)

    def draw(self, screen):
        current_frame = self.current_anim[int(self.frame_index)]
        sprite_rect = current_frame.get_rect(center=(self.position.x, self.position.y))
        
        if self.velocity.x < 0:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        screen.blit(current_frame, sprite_rect)
        self.render_hunger(screen)

def main():
    agents = [Agent() for _ in range(NUM_AGENTS)]
    food_list = []
    agents_to_remove = []  
    blood_pools = []  
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        screen.fill((100, 100, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # left mouse button
                food_pos = pygame.Vector2(pygame.mouse.get_pos())
                food_list.append(food_pos)

        for agent in agents_to_remove:
            if agent in agents:
                agents.remove(agent)  
                blood_pools.append(agent.position)  

   
        for pool_pos in blood_pools:
            pygame.draw.ellipse(screen, (139, 0, 0), (pool_pos.x -10, pool_pos.y -5 , 50, 10))

        for food in food_list:
            pygame.draw.ellipse(screen, (150, 75, 0), (food.x, food.y, FOOD_SIZE, FOOD_SIZE))

        for agent in agents:
            agent.update(food_list, agents, dt, agents_to_remove, blood_pools)
            agent.draw(screen)



        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
