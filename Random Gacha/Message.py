import random
import pygame

class Message:
    def __init__(self, text, position, color, screen_width, screen_height, fade_duration=4000):
        self.text = text
        self.position = list(position)
        self.velocity = [random.uniform(-2, 2), -5]
        self.font = pygame.font.Font(None, 36)
        self.start_time = pygame.time.get_ticks()  # time when message was created
        self.fade_duration = fade_duration  
        self.alpha = 255  # start with 100% opacity
        self.screen_width = screen_width  # store screen width
        self.screen_height = screen_height  # store screen height
        self.color = color  # store the color for rendering

    def update(self):
        # Simulate gravity
        self.velocity[1] += 0.2  # Gravity effect
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        # Calculate elapsed time and fade out
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time < self.fade_duration:
            self.alpha = 255 * (1 - (elapsed_time / self.fade_duration))  # decrease alpha over time //// fade fx
        else:
            self.alpha = 0  # Fully transparent after duration

        # Bounce off the edges of the screen
        if self.position[0] <= 0 or self.position[0] + self.get_width() >= self.screen_width:
            self.velocity[0] = -self.velocity[0] * 0.5  # lose momentum
        if self.position[1] + self.get_height() >= self.screen_height:
            self.velocity[1] = -self.velocity[1] * 0.5  # bounce and lose momentum  /// adapt from the older "ball project" for fun

    def get_width(self):
        return self.font.size(self.text)[0]
    
    def get_height(self):
        return self.font.size(self.text)[1]
    
    def draw(self, surface, offset=(0, 0)):
        """Draw the message on the surface with an optional offset for screen shake."""
        text_surface = self.font.render(self.text, True, self.color)  # Render the text
        text_surface.set_alpha(self.alpha)  # Set the alpha for fading
        # Apply the offset to the message position (for screen shake)
        position_with_offset = (self.position[0] + offset[0], self.position[1] + offset[1])
        # Draw the text surface at the offset position
        surface.blit(text_surface, position_with_offset)

    def is_expired(self):
        return self.alpha <= 0  # check if the message is 0% opacity so maingame can remove it
