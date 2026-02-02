import random

import pygame
from pygame.math import Vector2

width = 1000
height = 500
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# Initial
start_x = width / 2
start_y = height / 2


snake_body = [Vector2(start_x, start_y)]
cell = 25
speed = cell
velocity = Vector2(speed, 0)

apple = pygame.Surface((cell, cell))
apple.fill("Red")
apple_pos = Vector2(
    random.randrange(0, width, cell),
    random.randrange(0, height, cell)

)

while True:
    prev_velocity = velocity
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and velocity.length_squared() != 0:
            if event.key == pygame.K_LEFT:
                velocity = velocity.rotate(-90)
            elif event.key == pygame.K_RIGHT:
                velocity = velocity.rotate(90)
    if velocity.length_squared() != 0:
        old_head = snake_body[0].copy()
        snake_body[0] += velocity
        for i in range(1, len(snake_body)):
            temp = snake_body[i].copy()
            snake_body[i] = old_head
            old_head = temp
    head = snake_body[0]
    if head.x < 0 or head.x >= width or head.y < 0 or head.y >= height:
        snake_body = [Vector2(start_x, start_y)]
        velocity = Vector2(0, 0)
    if head in snake_body[1:]:
        snake_body = [Vector2(start_x, start_y)]
        velocity = Vector2(0, 0)
    if head == apple_pos or apple_pos in snake_body:
        apple_pos = Vector2(
            random.randrange(0, width, cell),
            random.randrange(0, height, cell)
        )
        snake_body.append(snake_body[-1].copy())
    screen.fill("Black")
    pygame.draw.rect(
        screen,
        "Yellow",
        (head.x, head.y, cell, cell)
    )
    for segment in snake_body[1:]:
        pygame.draw.rect(
            screen,
            "Green",
            (segment.x, segment.y, cell, cell)
        )

    screen.blit(apple, apple_pos)

    pygame.display.update()
    clock.tick(5)


