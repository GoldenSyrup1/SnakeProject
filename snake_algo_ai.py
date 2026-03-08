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

        # seed it with the head
        heapq.heappush(open_set, (0, 0, (int(snake_head.x), int(snake_head.y))))
        while open_set:
            f, g, current = heapq.heappop(open_set) # pop from open set to get current
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
                        i in snake) and not ((int(i.x), int(i.y)) in visited):
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

        pass

    def perturb(self, snake, apple):
        pass

    def get_next_move(self, snake, apple):
        pass


ai = SnakeAlgoAI(1000, 500, 25)
snake = [Vector2(500, 250), Vector2(500, 225), Vector2(500, 200)]
apple = Vector2(300, 100)
path = ai.astar(snake, apple)
for pos in path:
    print(pos)