import matplotlib.pyplot as plt
from pygame.math import Vector2
import heapq
class SnakeAlgoAI:
    def __init__(self, width, height, cell):
        self.width = width
        self.height = height
        self.cell = cell
        self.rows = height // cell
        self.cols = width // cell
        self.cycle, self.cycle_index = self.build_hamiltonian()

    def build_hamiltonian(self):
        cycle = []

        # Row 0 full width (top row)
        for col in range(self.cols):
            cycle.append(Vector2(col * self.cell, 0))

        # Rows 1 to last, skipping col 0 (left column reserved for return)
        for row in range(1, self.rows):
            cols = range(1, self.cols)
            if row % 2 == 0:
                cols = range(1, self.cols)
            else:
                cols = range(self.cols - 1, 0, -1)
            for col in cols:
                cycle.append(Vector2(col * self.cell, row * self.cell))

        # Return path up the left column (bottom to top, skipping (0,0) since it's already in)
        for row in range(self.rows - 1, 0, -1):
            cycle.append(Vector2(0, row * self.cell))

        cycle_index = {(int(v.x), int(v.y)): i for i, v in enumerate(cycle)}
        return cycle, cycle_index

    def next_in_cycle(self, pos):
        idx = self.cycle_index[(int(pos.x), int(pos.y))]
        return self.cycle[(idx + 1) % len(self.cycle)]

    def astar(self, snake, apple):
        # snake = [Vector2(start_x, start_y)], a bunch of positions.
        # apple = Vector2(apple_x, apple_y)
        # start_pos = snake head: Vector2(x,y)
        # end_pos = apple: Vector2(a,b)
        path = [snake[0]]
        start = path[-1]
        neg_x = False
        neg_y = False
        change_x = self.cell
        change_y = self.cell
        # calculates horizontal steps based on grid

        left = snake[0] + Vector2(-self.cell, 0)
        right = snake[0] + Vector2(self.cell, 0)
        up = snake[0] + Vector2(0, -self.cell)
        down = snake[0] + Vector2(0, self.cell)
        cardinal_directions = [left, right, up, down]
        valid_directions = []
        for i in cardinal_directions:
            if not ((i.x < 0 or i.x > self.width) or (i.y < 0 or i.y > self.height)) and not (i in snake) and not(i in path):
                valid_directions.append(i)
        scores = {(int(v.x), int(v.y)): 0 for v in valid_directions}
        for j in scores.keys():
            no_of_movements_x = abs((apple.x - j[0]) / self.cell)
            no_of_movements_y = abs((apple.y - j[1]) / self.cell)
            h = no_of_movements_x + no_of_movements_y
            g = 1
            scores[j] = g+h
            pass
        # For now, return none
        return None


    def survival_check(self, snake, path):
        pass

    def perturb(self, snake, apple):
        pass

    def get_next_move(self, snake, apple):
        pass


ai = SnakeAlgoAI(1000, 500, 25)
snake = [Vector2(500, 250)]
apple = Vector2(300, 100)
path = ai.astar(snake, apple)
for pos in path:
    print(pos)