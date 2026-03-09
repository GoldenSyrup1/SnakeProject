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
        snake_head = snake[0]

        open_set = []  # lives outside the while loop
        visited = set()  # tracks what's already been expanded
        came_from = {}  # tracks where each node came from
        steps = 0 # limiter
        # seed it with the head
        heapq.heappush(open_set, (0, 0, (int(snake_head.x), int(snake_head.y))))
        while open_set:
            steps += 1
            if steps > self.rows * self.cols:

                return None
            f, g, current = heapq.heappop(open_set) # pop from open set to get current
            if current in visited:  # ADD THIS
                continue

            if current == (int(apple.x), int(apple.y)):

                path = []
                while current != (int(snake_head.x), int(snake_head.y)):
                    path.append(Vector2(current[0], current[1]))
                    current = came_from[current]
                path.append(snake_head)
                return path[::-1] # reverse searching the path
            visited.add(current)
            # create 4 cardinal directions
            current_vec = Vector2(current[0], current[1])
            left = current_vec + Vector2(-self.cell, 0)
            right = current_vec + Vector2(self.cell, 0)
            up = current_vec + Vector2(0, -self.cell)
            down = current_vec + Vector2(0, self.cell)
            cardinal_directions = [left, right, up, down]
            valid_directions = []
            # check if there is anything they have explored or interfered with
            for i in cardinal_directions:
                if not ((i.x < 0 or i.x >= self.width) or (i.y < 0 or i.y >= self.height)) and not (
                        i in snake[:-1]) and not ((int(i.x), int(i.y)) in visited):
                    valid_directions.append(i)

            for neighbor in valid_directions:
                # manhattan distance
                h = (abs(neighbor.x - apple.x) + abs(neighbor.y - apple.y)) / self.cell
                # associate each node with f = g+h, g+1, and neighbor node.
                # make the start the best node now while keeping other nodes to explore for boundaries and stuff.
                heapq.heappush(open_set, (g + h, g + 1, (int(neighbor.x), int(neighbor.y))))
                # update dictionary with the lowest score f vector
                came_from[(int(neighbor.x), int(neighbor.y))] = current




        # return None if no such path exists
        return None

    def survival_check(self, snake, path):
        if path is None:
            return False
        sim_snake = snake.copy()
        for i in range(1, len(path) - 1):  # stop one before apple
            new_head = path[i]
            sim_snake = [new_head] + sim_snake[:-1]  # normal move, pop tail
        # final step: eat apple, don't pop tail
        sim_snake = [path[-1]] + sim_snake  # grow
        result = self.astar(sim_snake, sim_snake[-1])
        return result is not None

    def perturb(self, snake, apple):
        # snake = [Vector2(start_x, start_y), Vector2(tail_end_x, tail_end_y)], a bunch of positions.
        # apple = Vector2(apple_x, apple_y)
        head_idx = self.cycle_index[(int(snake[0].x), int(snake[0].y))]
        tail_idx = self.cycle_index[(int(snake[-1].x), int(snake[-1].y))]
        # get cardinal directions
        head = snake[0]
        left = head + Vector2(-self.cell, 0)
        right = head + Vector2(self.cell, 0)
        up = head + Vector2(0, -self.cell)
        down = head + Vector2(0, self.cell)
        cardinal_directions = [left, right, up, down]
        valid_directions = []
        # check if there is anything they have explored or interfered with
        for i in cardinal_directions:
            if not ((i.x < 0 or i.x >= self.width) or (i.y < 0 or i.y >= self.height)) and not (
                    i in snake[:-1]):
                valid_directions.append(i)
        valid_shortcuts = []
        for neighbor in valid_directions:
            # is neighbor ahead of head but before tail in cycle order?
            neighbor_idx = self.cycle_index[(int(neighbor.x), int(neighbor.y))]
            if (neighbor_idx - head_idx) % len(self.cycle) < (tail_idx - head_idx) % len(self.cycle):
                valid_shortcuts.append(neighbor)
        if not valid_shortcuts:
            return None
        return min(valid_shortcuts, key=lambda n: abs(n.x - apple.x) + abs(n.y - apple.y))

    def get_next_move(self, snake, apple):
        path = self.astar(snake, apple)
        survival_boolean = self.survival_check(snake, path)

        if survival_boolean:
            return path[1]
        else:
            shortcut = self.perturb(snake,apple)
            if shortcut is not None:
                return shortcut
        return self.next_in_cycle(snake[0])



