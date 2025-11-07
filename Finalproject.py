import pygame
import random
import sys

pygame.init()

# --- Screen setup ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dorm Dash")
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
RED = (220, 50, 50)
GREEN = (70, 200, 70)
YELLOW = (250, 230, 80)
GRAY = (60, 60, 60)

# --- Player setup ---
player = pygame.Rect(50, HEIGHT - 80, 40, 40)
player_speed = 4

# --- Teachers (enemies) ---
teachers = []
for _ in range(3):
    rect = pygame.Rect(random.randint(200, WIDTH - 100),
                       random.randint(100, HEIGHT - 200), 40, 40)
    dx = random.choice([-3, 3])
    dy = random.choice([-3, 3])
    teachers.append([rect, dx, dy])

# --- Tokens ---
tokens = []
for _ in range(3):
    x = random.randint(100, WIDTH - 100)
    y = random.randint(100, HEIGHT - 100)
    tokens.append(pygame.Rect(x, y, 20, 20))

# --- Goal ---
goal = pygame.Rect(WIDTH - 100, 40, 60, 60)

# --- Maze walls (list of rectangles) ---
walls = [
    pygame.Rect(0, 0, WIDTH, 20),  # top
    pygame.Rect(0, 0, 20, HEIGHT),  # left
    pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),  # right
    pygame.Rect(0, HEIGHT - 20, WIDTH, 20),  # bottom
    pygame.Rect(100, 100, 600, 20),
    pygame.Rect(100, 200, 20, 300),
    pygame.Rect(200, 300, 400, 20),
    pygame.Rect(700, 150, 20, 400),
    pygame.Rect(300, 150, 20, 200),
    pygame.Rect(500, 400, 20, 150)
]

# --- Game state ---
tokens_collected = 0
game_over = False
won = False
font = pygame.font.SysFont(None, 36)

# --- Helper: handle collision with walls ---
def move_player(rect, dx, dy):
    rect.x += dx
    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0:  # moving right
                rect.right = wall.left
            if dx < 0:  # moving left
                rect.left = wall.right
    rect.y += dy
    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0:  # moving down
                rect.bottom = wall.top
            if dy < 0:  # moving up
                rect.top = wall.bottom

# --- Main game loop ---
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

        # Move teachers
        for t in teachers:
            rect, vx, vy = t
            rect.x += vx
            rect.y += vy
            # Bounce on walls
            for wall in walls:
                if rect.colliderect(wall):
                    t[1] = -vx
                    t[2] = -vy
            if rect.left < 20 or rect.right > WIDTH - 20:
                t[1] = -vx
            if rect.top < 20 or rect.bottom > HEIGHT - 20:
                t[2] = -vy

        # Check teacher collision
        for rect, vx, vy in teachers:
            if player.colliderect(rect):
                game_over = True

        # Collect tokens
        for t in tokens[:]:
            if player.colliderect(t):
                tokens.remove(t)
                tokens_collected += 1

        # Check goal
        if player.colliderect(goal):
            won = True
            game_over = True

    # --- Draw everything ---
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)
    pygame.draw.rect(screen, GREEN, goal)
    for t in tokens:
        pygame.draw.rect(screen, YELLOW, t)
    for rect, vx, vy in teachers:
        pygame.draw.rect(screen, RED, rect)
    pygame.draw.rect(screen, BLUE, player)

    text = font.render(f"Tokens: {tokens_collected}", True, WHITE)
    screen.blit(text, (10, 10))

    if game_over:
        if won:
            msg = font.render("You made it to Assembly! 🎉", True, WHITE)
        else:
            msg = font.render("Caught by a teacher! Press R to restart.", True, WHITE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
        if keys[pygame.K_r]:
            player.topleft = (50, HEIGHT - 80)
            tokens_collected = 0
            tokens = [pygame.Rect(random.randint(100, WIDTH - 100),
                                  random.randint(100, HEIGHT - 100), 20, 20)
                      for _ in range(3)]
            game_over = False
            won = False

    pygame.display.flip()

