import pygame
from pygame.math import Vector2
from snake_algo_ai import SnakeAlgoAI

width = 1000
height = 500
cell = 25

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Hamiltonian Cycle Test")
clock = pygame.time.Clock()

ai = SnakeAlgoAI(width, height, cell)

snake_body = [Vector2(0, 0)]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Move head to next position in cycle
    next_pos = ai.next_in_cycle(snake_body[0])
    snake_body.insert(0, next_pos)
    if len(snake_body) > 10:  # trail of 10 to visualize direction
        snake_body.pop()

    screen.fill("Black")
    for i, seg in enumerate(snake_body):
        color = "Yellow" if i == 0 else "Green"
        pygame.draw.rect(screen, color, (seg.x, seg.y, cell, cell))

    pygame.display.update()
    clock.tick(30)