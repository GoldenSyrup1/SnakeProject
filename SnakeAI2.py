import pygame
from pygame.math import Vector2
import time
from SnakeAI import SnakeEnv, get_q

pygame.init()
screen = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("Snake AI Playing")
clock = pygame.time.Clock()

env = SnakeEnv()
state = env.reset()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # AI chooses best action (no randomness)
    q = get_q(state)
    action = q.index(max(q))

    state, reward, done = env.step(action)

    if done:
        time.sleep(0.5)
        state = env.reset()

    # ---- DRAW ----
    screen.fill("black")

    # apple
    pygame.draw.rect(
        screen, "red",
        (*env.apple, env.cell, env.cell)
    )

    # snake
    for i, seg in enumerate(env.snake):
        color = "yellow" if i == 0 else "green"
        pygame.draw.rect(
            screen, color,
            (seg.x, seg.y, env.cell, env.cell)
        )

    pygame.display.update()
    clock.tick(10)

pygame.quit()




