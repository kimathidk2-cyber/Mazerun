import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dorm Dash")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 120, 255)
RED = (220, 60, 60)
GREEN = (80, 200, 80)
YELLOW = (255, 230, 90)
GRAY = (40, 40, 50)

player = pygame.Rect(40, HEIGHT - 80, 40, 40)
player_speed = 4

teachers = []
for _ in range(4):
    rect = pygame.Rect(
        random.randint(200, WIDTH - 100),
        random.randint(100, HEIGHT - 200),
        40,
        40
    )
    teachers.append(rect)

teacher_directions = [
    (random.choice([-3, 3]), random.choice([-3, 3]))
    for _ in teachers
]

tokens = []
for _ in range(3):
    x = random.randint(100, WIDTH - 100)
    y = random.randint(100, HEIGHT - 100)
    tokens.append(pygame.Rect(x, y, 20, 20))

goal = pygame.Rect(WIDTH - 100, 40, 60, 60)

walls = [
    # Outer borders
    pygame.Rect(0, 0, WIDTH, 20),
    pygame.Rect(0, HEIGHT - 20, WIDTH, 20),
    pygame.Rect(0, 0, 20, HEIGHT),
    pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),

    # Top maze section
    pygame.Rect(100, 80, 600, 20),      # Long top wall
    pygame.Rect(100, 80, 20, 180),      # Left vertical down
    pygame.Rect(680, 80, 20, 220),      # Right vertical down
    pygame.Rect(200, 160, 400, 20),     # Mid horizontal
    pygame.Rect(200, 160, 20, 200),     # Left vertical
    pygame.Rect(580, 160, 20, 200),     # Right vertical
    pygame.Rect(260, 260, 260, 20),     # Horizontal connector

    # Middle band with two gaps (at x < 100 and x between 350–450)
    pygame.Rect(100, 360, 250, 20),
    pygame.Rect(450, 360, 250, 20),

    # Lower maze section trapping careless paths
    pygame.Rect(100, 440, 600, 20),
    pygame.Rect(100, 440, 20, 120),
    pygame.Rect(680, 440, 20, 120),
]

tokens_collected = 0
game_over = False
won = False
font = pygame.font.SysFont(None, 36)


def move_player(rect, dx, dy):
    rect.x += dx
    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0:
                rect.right = wall.left
            if dx < 0:
                rect.left = wall.right

    rect.y += dy
    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0:
                rect.bottom = wall.top
            if dy < 0:
                rect.top = wall.bottom


running = True
while running:
    clock.tick(60)
    screen.fill(GRAY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if not game_over:
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = player_speed

        move_player(player, dx, dy)

        for i, rect in enumerate(teachers):
            # Occasionally change direction
            if random.randint(0, 60) == 0:
                teacher_directions[i] = (
                    random.choice([-3, 0, 3]),
                    random.choice([-3, 0, 3])
                )

            vx, vy = teacher_directions[i]
            rect.x += vx
            rect.y += vy

            # Bounce off walls
            for wall in walls:
                if rect.colliderect(wall):
                    rect.x -= vx
                    rect.y -= vy
                    teacher_directions[i] = (-vx, -vy)

            # Keep inside inner border
            if rect.left < 20 or rect.right > WIDTH - 20:
                teacher_directions[i] = (-vx, vy)
            if rect.top < 20 or rect.bottom > HEIGHT - 20:
                teacher_directions[i] = (vx, -vy)

        # Collision: player with teachers
        for rect in teachers:
            if player.colliderect(rect):
                game_over = True

        # Collect tokens
        for t in tokens[:]:
            if player.colliderect(t):
                tokens.remove(t)
                tokens_collected += 1

        # Reach goal
        if player.colliderect(goal):
            won = True
            game_over = True

    # Draw everything
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)
    pygame.draw.rect(screen, GREEN, goal)

    for t in tokens:
        pygame.draw.rect(screen, YELLOW, t)

    for rect in teachers:
        pygame.draw.rect(screen, RED, rect)

    pygame.draw.rect(screen, BLUE, player)

    text = font.render(f"Tokens: {tokens_collected}", True, WHITE)
    screen.blit(text, (10, 10))

    if game_over:
        if won:
            msg = font.render("You made it to Assembly! 🎉", True, WHITE)
        else:
            msg = font.render("Caught by Mx. Elle! Press R to restart.", True, WHITE)

        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

        if keys[pygame.K_r]:
            # Reset player
            player.topleft = (40, HEIGHT - 80)

            # Reset tokens
            tokens_collected = 0
            tokens = [
                pygame.Rect(
                    random.randint(100, WIDTH - 100),
                    random.randint(100, HEIGHT - 100),
                    20,
                    20
                )
                for _ in range(3)
            ]

            # Reset teacher positions and directions
            for rect in teachers:
                rect.x = random.randint(200, WIDTH - 100)
                rect.y = random.randint(100, HEIGHT - 200)

            teacher_directions = [
                (random.choice([-3, 3]), random.choice([-3, 3]))
                for _ in teachers
            ]

            game_over = False
            won = False

    pygame.display.flip()
