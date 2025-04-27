import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("William's Flight Practice")

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Load images
background_img = pygame.image.load("background_forest.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

william_img = pygame.image.load("william_bird.png")
william_img = pygame.transform.scale(william_img, (60, 45))
william_rect = william_img.get_rect(center=(100, HEIGHT // 2))

branch_img = pygame.image.load("branch.png")
branch_img = pygame.transform.scale(branch_img, (200, 40))

# Physics
gravity = 0.5
flap_strength = -10
velocity = 0

# Branch settings
branch_width = 200
branch_height = 40
branch_x = WIDTH - branch_width - 50
branch_y = random.randint(200, 400)

# Font
font = pygame.font.SysFont(None, 48)

# Game states
game_over = False
landed = False

# Main game loop
while True:
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                velocity = flap_strength

    if not game_over:
        # Apply gravity
        velocity += gravity
        william_rect.y += int(velocity)

        # Draw branch
        screen.blit(branch_img, (branch_x, branch_y))

        # Collision detection
        if william_rect.colliderect((branch_x, branch_y, branch_width, branch_height)):
            if abs(velocity) < 5:
                landed = True
                game_over = True
            else:
                game_over = True

        # Check boundaries
        if william_rect.top <= 0 or william_rect.bottom >= HEIGHT:
            game_over = True

    # Draw William
    screen.blit(william_img, william_rect)

    if game_over:
        if landed:
            text = font.render("Safe Landing! ✨", True, GREEN)
        else:
            text = font.render("Crash! 😟", True, (255, 0, 0))
        screen.blit(
            text,
            (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2),
        )

    pygame.display.update()
    clock.tick(FPS)
