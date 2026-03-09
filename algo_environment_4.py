import random
import pygame
from pygame.math import Vector2
from snake_algo_additional3 import SnakeAlgoAI

width = 1000
height = 500
cell = 25

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

start_x = width // 2
start_y = height // 2

snake_body = [Vector2(start_x, start_y)]

apple = pygame.Surface((cell, cell))
apple.fill("Red")


def spawn_apple(snake_body):
    while True:
        pos = Vector2(
            random.randrange(0, width, cell),
            random.randrange(0, height, cell)
        )
        if pos not in snake_body:
            return pos


def draw_hamiltonian_cycle(screen, ai):
    cycle = ai.cycle

    for i in range(len(cycle)):
        start = cycle[i]
        end = cycle[(i + 1) % len(cycle)]

        start_pos = (int(start.x + cell // 2), int(start.y + cell // 2))
        end_pos = (int(end.x + cell // 2), int(end.y + cell // 2))

        pygame.draw.line(screen, (60, 60, 60), start_pos, end_pos, 2)

    # Optional: draw small dots on cycle nodes
    for node in cycle:
        center = (int(node.x + cell // 2), int(node.y + cell // 2))
        pygame.draw.circle(screen, (90, 90, 90), center, 2)


apple_pos = spawn_apple(snake_body)
AI = SnakeAlgoAI(width, height, cell)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    next_cell = AI.get_next_move(snake_body, apple_pos)

    if next_cell is None:
        pygame.quit()
        raise SystemExit

    snake_body.insert(0, next_cell)

    if next_cell == apple_pos:
        apple_pos = spawn_apple(snake_body)
    else:
        snake_body.pop()

    head = snake_body[0]

    if head.x < 0 or head.x >= width or head.y < 0 or head.y >= height:
        snake_body = [Vector2(start_x, start_y)]
        apple_pos = spawn_apple(snake_body)

    elif head in snake_body[1:]:
        snake_body = [Vector2(start_x, start_y)]
        apple_pos = spawn_apple(snake_body)

    screen.fill("Black")

    draw_hamiltonian_cycle(screen, AI)

    pygame.draw.rect(screen, "Yellow", (head.x, head.y, cell, cell))

    for segment in snake_body[1:]:
        pygame.draw.rect(screen, "Green", (segment.x, segment.y, cell, cell))

    screen.blit(apple, apple_pos)

    pygame.display.update()
    clock.tick(960)