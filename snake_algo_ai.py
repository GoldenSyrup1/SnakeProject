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

        for col in range(self.cols):
            cycle.append(Vector2(col * self.cell, 0))

        for row in range(1, self.rows):
            if row % 2 == 0:
                cols = range(1, self.cols)
            else:
                cols = range(self.cols - 1, 0, -1)
            for col in cols:
                cycle.append(Vector2(col * self.cell, row * self.cell))

        for row in range(self.rows - 1, 0, -1):
            cycle.append(Vector2(0, row * self.cell))

        # Duplicate check
        coords = [(int(v.x), int(v.y)) for v in cycle]
        duplicates = [c for c in coords if coords.count(c) > 1]
        if duplicates:
            print(f"DUPLICATES FOUND: {set(duplicates)}")
        else:
            print("No duplicates")

        # Adjacency check
        for i in range(len(cycle)):
            a = cycle[i]
            b = cycle[(i + 1) % len(cycle)]
            diff = abs(a.x - b.x) + abs(a.y - b.y)
            if diff != self.cell:
                print(f"BROKEN LINK at index {i}: {a} -> {b}, diff={diff}")

        print(f"Cycle length: {len(cycle)}, Expected: {self.rows * self.cols}")

        cycle_index = {(int(v.x), int(v.y)): i for i, v in enumerate(cycle)}
        return cycle, cycle_index

    def next_in_cycle(self, pos):
        idx = self.cycle_index[(int(pos.x), int(pos.y))]
        next_pos = self.cycle[(idx + 1) % len(self.cycle)]

        # Safety check: next must be adjacent to current head
        diff = abs(next_pos.x - pos.x) + abs(next_pos.y - pos.y)
        if diff != self.cell:
            print(f"CYCLE BROKEN: head={pos}, next={next_pos}, diff={diff}")

        return next_pos

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

    def flood_fill_count(self, snake):
        """Count reachable cells from head, given current snake body as obstacles."""
        head = snake[0]
        body_set = set((int(s.x), int(s.y)) for s in snake[1:])
        start = (int(head.x), int(head.y))
        visited = {start}
        queue = [start]
        while queue:
            cx, cy = queue.pop()
            for dx, dy in [(self.cell, 0), (-self.cell, 0), (0, self.cell), (0, -self.cell)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in body_set and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return len(visited)

    def survival_check(self, snake, path):
        if path is None:
            return False
        sim_snake = snake.copy()
        for i in range(1, len(path) - 1):
            new_head = path[i]
            sim_snake = [new_head] + sim_snake[:-1]
        sim_snake = [path[-1]] + sim_snake  # eat apple, grow

        # Check 1: can reach tail
        if self.astar(sim_snake, sim_snake[-1]) is None:
            return False
        # Check 2: enough open space (at least snake length)
        if self.flood_fill_count(sim_snake) < len(sim_snake):
            return False
        return True

    def perturb(self, snake, apple):
        head_idx = self.cycle_index[(int(snake[0].x), int(snake[0].y))]
        tail_idx = self.cycle_index[(int(snake[-1].x), int(snake[-1].y))]
        head = snake[0]
        cardinal_directions = [
            head + Vector2(-self.cell, 0),
            head + Vector2(self.cell, 0),
            head + Vector2(0, -self.cell),
            head + Vector2(0, self.cell)
        ]
        valid_shortcuts = []
        for neighbor in cardinal_directions:
            if (neighbor.x < 0 or neighbor.x >= self.width or
                    neighbor.y < 0 or neighbor.y >= self.height):
                continue
            if neighbor in snake[:-1]:
                continue
            neighbor_idx = self.cycle_index[(int(neighbor.x), int(neighbor.y))]
            if (neighbor_idx - head_idx) % len(self.cycle) < (tail_idx - head_idx) % len(self.cycle):
                # Simulate moving there and check flood fill
                sim_snake = [neighbor] + snake[:-1]
                if self.flood_fill_count(sim_snake) >= len(sim_snake):
                    valid_shortcuts.append(neighbor)
        if not valid_shortcuts:
            return None
        return min(valid_shortcuts, key=lambda n: abs(n.x - apple.x) + abs(n.y - apple.y))

    def get_next_move(self, snake, apple):
        path = self.astar(snake, apple)
        fill = self.flood_fill_count(snake)
        print(f"Head={snake[0]}, len={len(snake)}, free={fill}")
        if path and self.survival_check(snake, path):
            print("Tier 1: A*")
            return path[1]

        shortcut = self.perturb(snake, apple)
        if shortcut is not None:
            print("Tier 2: Perturb")
            return shortcut

        # Tier 3: find the next safe cycle step
        head = snake[0]
        body_set = set((int(s.x), int(s.y)) for s in snake[1:])
        idx = self.cycle_index[(int(head.x), int(head.y))]

        for offset in range(1, len(self.cycle)):
            candidate = self.cycle[(idx + offset) % len(self.cycle)]
            cx, cy = int(candidate.x), int(candidate.y)
            # Must be adjacent to head AND not in body
            if abs(candidate.x - head.x) + abs(candidate.y - head.y) == self.cell:
                if (cx, cy) not in body_set:
                    print("Tier 3: Hamiltonian")
                    return candidate

        # Absolute last resort: any free neighbor
        print("Tier 3: Emergency")
        for dx, dy in [(self.cell, 0), (-self.cell, 0), (0, self.cell), (0, -self.cell)]:
            nb = Vector2(head.x + dx, head.y + dy)
            if 0 <= nb.x < self.width and 0 <= nb.y < self.height:
                if (int(nb.x), int(nb.y)) not in body_set:
                    return nb

        return self.cycle[(idx + 1) % len(self.cycle)]  # truly stuck, die gracefully



