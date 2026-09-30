import random
import sys
from collections import deque

import pygame

pygame.init()

CELL = 20
COLS, ROWS = 30, 30
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL
MOVE_INTERVAL = 240  # ms per snake step

BG = (18, 18, 24)
GRID = (26, 26, 34)
HEAD_COLOR = (130, 230, 140)
BODY_COLOR = (60, 165, 95)
FOOD_COLOR = (235, 90, 90)
TEXT_COLOR = (230, 230, 240)

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
KEYS = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 56)
small_font = pygame.font.SysFont(None, 28)


def cell_rect(col, row):
    return pygame.Rect(col * CELL, row * CELL, CELL, CELL)


def random_food(snake):
    free = [(c, r) for c in range(COLS) for r in range(ROWS) if (c, r) not in snake]
    return random.choice(free) if free else None


def reset():
    mid = (COLS // 2, ROWS // 2)
    snake = [mid, (mid[0] - 1, mid[1]), (mid[0] - 2, mid[1])]
    return snake, random_food(snake)


snake, food = reset()
direction = RIGHT
pending = deque()
score = 0
accumulator = 0
state = "playing"

running = True
while running:
    dt = clock.tick(60)

    # ---------- input ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if state == "playing" and event.key in KEYS:
                new_dir = KEYS[event.key]
                last = pending[-1] if pending else direction
                opposite = (new_dir[0] + last[0], new_dir[1] + last[1]) == (0, 0)
                if not opposite and new_dir != last and len(pending) < 2:
                    pending.append(new_dir)

            elif state == "gameover" and event.key in (pygame.K_r, pygame.K_SPACE):
                snake, food = reset()
                direction = RIGHT
                pending.clear()
                score = 0
                accumulator = 0
                state = "playing"

    # ---------- simulate ----------
    if state == "playing":
        accumulator += dt
        while accumulator >= MOVE_INTERVAL:
            accumulator -= MOVE_INTERVAL

            if pending:
                direction = pending.popleft()

            hx, hy = snake[0]
            new_head = (hx + direction[0], hy + direction[1])

            # wall
            if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
                state = "gameover"
                break

            eating = new_head == food
            body = snake if eating else snake[:-1]
            if new_head in body:
                state = "gameover"
                break

            snake.insert(0, new_head)
            if eating:
                score += 1
                food = random_food(snake)
            else:
                snake.pop()

    # ---------- draw ----------
    screen.fill(BG)

    for c in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRID, (c, 0), (c, HEIGHT))
    for r in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRID, (0, r), (WIDTH, r))

    if food:
        pygame.draw.rect(screen, FOOD_COLOR, cell_rect(*food), border_radius=6)

    for i, (col, row) in enumerate(snake):
        color = HEAD_COLOR if i == 0 else BODY_COLOR
        pygame.draw.rect(screen, color, cell_rect(col, row), border_radius=4)

    screen.blit(small_font.render(f"Score: {score}", True, TEXT_COLOR), (10, 10))

    if state == "gameover":
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        screen.blit(shade, (0, 0))

        over = font.render("Game Over", True, TEXT_COLOR)
        screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

        hint = small_font.render("Press R to play again", True, TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))

    pygame.display.flip()

pygame.quit()
sys.exit()
