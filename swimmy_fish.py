import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920
GRAVITY = 1
FISH_JUMP = 15
OBSTACLE_GAP = 800  # Increased gap size between rocks
OBSTACLE_SPEED = 4
SPAWN_OBSTACLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_OBSTACLE_EVENT, 1500)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Swimmy Fish")

# Load font for score display
font = pygame.font.Font(None, 36)

# Fish class


class Fish(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("fish.png").convert_alpha()
        self.image = pygame.transform.scale(
            self.image, (self.image.get_width() // 2, self.image.get_height() // 2))
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT // 2))
        self.velocity = 0

    def swim(self):
        self.velocity = -FISH_JUMP

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        if self.rect.top <= 0:
            self.rect.y = 1
            self.velocity = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - self.rect.height - 1
            self.velocity = 0

# Obstacle class


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, position, gap_start):
        super().__init__()
        self.image_top = pygame.image.load("rock.png").convert_alpha()
        self.image_top = pygame.transform.scale(
            self.image_top, (100, gap_start))
        self.image_bottom = pygame.image.load("rock.png").convert_alpha()
        self.image_bottom = pygame.transform.scale(
            self.image_bottom, (100, SCREEN_HEIGHT - gap_start - OBSTACLE_GAP))

        self.rect_top = self.image_top.get_rect(
            midbottom=(position, gap_start))
        self.rect_bottom = self.image_bottom.get_rect(
            midtop=(position, gap_start + OBSTACLE_GAP))

        # Add margin to rects
        margin = 5
        self.rect_top.inflate_ip(-margin, -margin)
        self.rect_bottom.inflate_ip(-margin, -margin)

    def update(self, fish_group):
        global score
        self.rect_top.x -= OBSTACLE_SPEED
        self.rect_bottom.x -= OBSTACLE_SPEED
        if self.rect_top.right < 0:
            self.kill()
            score += 1  # Increment the score when an obstacle goes off the screen

    def draw(self, screen):
        screen.blit(self.image_top, self.rect_top)
        screen.blit(self.image_bottom, self.rect_bottom)


def check_collisions(fish, obstacles):
    for obstacle in obstacles:
        if fish.rect.colliderect(obstacle.rect_top) or fish.rect.colliderect(obstacle.rect_bottom):
            fish_center_x = fish.rect.centerx
            top_obstacle_right = obstacle.rect_top.right
            top_obstacle_left = obstacle.rect_top.left

            if top_obstacle_left <= fish_center_x <= top_obstacle_right:
                return True
    return False


# Create fish and obstacle groups
fish_group = pygame.sprite.GroupSingle()
fish_group.add(Fish())

obstacle_group = pygame.sprite.Group()

# Main game loop
score = 0
game_over = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            fish_group.sprites()[0].swim()
        if event.type == SPAWN_OBSTACLE_EVENT and not game_over:
            gap_start = random.randint(200, SCREEN_HEIGHT - OBSTACLE_GAP - 200)
            obstacle_group.add(Obstacle(SCREEN_WIDTH, gap_start))

    # Update fish and obstacle positions
    fish_group.update()
    # Pass the fish_group to the update() method of the obstacle_group
    obstacle_group.update(fish_group)

    # Check for collisions
    if check_collisions(fish_group.sprites()[0], obstacle_group):
        game_over = True
        obstacle_group.empty()

    # Draw background and sprites
    screen.fill((0, 0, 0))
    fish_group.draw(screen)
    for obstacle in obstacle_group:
        obstacle.draw(screen)

    # Draw score
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    # Position the score text just below the top-right corner
    screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

    # Refresh display
    pygame.display.update()

    # Cap frame rate
    pygame.time.Clock().tick(60)

    # Game over behavior
    if game_over:
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        restart_text = font.render("Click to restart", True, (255, 255, 255))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() //
                    2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() //
                    2, SCREEN_HEIGHT // 2 + restart_text.get_height()))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_over = False
                score = 0
                fish_group.empty()
                fish_group.add(Fish())
