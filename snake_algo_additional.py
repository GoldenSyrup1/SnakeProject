from pygame.math import Vector2
import heapq


class SnakeAlgoAI:
    def __init__(self, width, height, cell):
        self.width = width
        self.height = height
        self.cell = cell
        self.rows = height // cell
        self.cols = width // cell

        if self.rows % 2 != 0 and self.cols % 2 != 0:
            raise ValueError(
                "Hamiltonian cycle requires at least one of rows or cols to be even."
            )

        self.directions = [
            Vector2(-cell, 0),
            Vector2(cell, 0),
            Vector2(0, -cell),
            Vector2(0, cell),
        ]

        self.cycle, self.cycle_index = self.build_hamiltonian()

    def build_hamiltonian(self):
        cycle = []

        for col in range(self.cols):
            cycle.append(Vector2(col * self.cell, 0))

        for row in range(1, self.rows):
            if row % 2 == 1:
                col_range = range(self.cols - 1, 0, -1)
            else:
                col_range = range(1, self.cols)

            for col in col_range:
                cycle.append(Vector2(col * self.cell, row * self.cell))

        for row in range(self.rows - 1, 0, -1):
            cycle.append(Vector2(0, row * self.cell))

        cycle_index = {(int(v.x), int(v.y)): i for i, v in enumerate(cycle)}
        return cycle, cycle_index

    def _vec_key(self, vec):
        return int(vec.x), int(vec.y)

    def _in_bounds(self, pos):
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def next_in_cycle(self, pos):
        idx = self.cycle_index[self._vec_key(pos)]
        return self.cycle[(idx + 1) % len(self.cycle)]

    def cycle_distance(self, start, end):
        start_idx = self.cycle_index[self._vec_key(start)]
        end_idx = self.cycle_index[self._vec_key(end)]
        return (end_idx - start_idx) % len(self.cycle)

    def astar(self, snake, apple):
        if not snake:
            return None

        snake_head = snake[0]
        start_key = self._vec_key(snake_head)
        goal_key = self._vec_key(apple)

        blocked = {self._vec_key(v) for v in snake[:-1]}

        open_set = []
        heapq.heappush(open_set, (0, 0, start_key))

        came_from = {}
        g_score = {start_key: 0}
        visited = set()

        while open_set:
            f, g, current = heapq.heappop(open_set)

            if current in visited:
                continue
            visited.add(current)

            if current == goal_key:
                path = []
                node = current
                while node != start_key:
                    path.append(Vector2(node[0], node[1]))
                    node = came_from[node]
                path.append(Vector2(start_key[0], start_key[1]))
                path.reverse()
                return path

            current_vec = Vector2(current[0], current[1])

            for direction in self.directions:
                neighbor = current_vec + direction
                neighbor_key = self._vec_key(neighbor)

                if not self._in_bounds(neighbor):
                    continue
                if neighbor_key in blocked and neighbor_key != goal_key:
                    continue
                if neighbor_key in visited:
                    continue

                tentative_g = g + 1

                if neighbor_key not in g_score or tentative_g < g_score[neighbor_key]:
                    g_score[neighbor_key] = tentative_g
                    came_from[neighbor_key] = current
                    h = (
                        abs(neighbor.x - apple.x) + abs(neighbor.y - apple.y)
                    ) / self.cell
                    heapq.heappush(open_set, (tentative_g + h, tentative_g, neighbor_key))

        return None

    def survival_check(self, snake, path):
        if path is None:
            return False

        sim_snake = [segment.copy() for segment in snake]

        for i in range(1, len(path) - 1):
            new_head = path[i]
            sim_snake = [new_head] + sim_snake[:-1]

        sim_snake = [path[-1]] + sim_snake

        tail = sim_snake[-1]
        return self.astar(sim_snake, tail) is not None

    def perturb(self, snake, apple):
        head = snake[0]
        tail = snake[-1]

        head_idx = self.cycle_index[self._vec_key(head)]
        tail_idx = self.cycle_index[self._vec_key(tail)]

        blocked = {self._vec_key(v) for v in snake[:-1]}
        valid_shortcuts = []

        for direction in self.directions:
            neighbor = head + direction
            neighbor_key = self._vec_key(neighbor)

            if not self._in_bounds(neighbor):
                continue
            if neighbor_key in blocked:
                continue

            neighbor_idx = self.cycle_index[neighbor_key]
            dist_head_to_neighbor = (neighbor_idx - head_idx) % len(self.cycle)
            dist_head_to_tail = (tail_idx - head_idx) % len(self.cycle)

            if 0 < dist_head_to_neighbor < dist_head_to_tail:
                valid_shortcuts.append(neighbor)

        if not valid_shortcuts:
            return None

        return min(
            valid_shortcuts,
            key=lambda n: abs(n.x - apple.x) + abs(n.y - apple.y)
        )

    def longest_path_move(self, snake, apple):
        """
        Optional upgrade:
        Instead of taking the shortest safe path to the apple,
        try to take the longest safe detour while still progressing.

        This slows down apple collection slightly, but makes the snake
        much better at filling the board without boxing itself in.
        """
        head = snake[0]
        tail = snake[-1]

        blocked = {self._vec_key(v) for v in snake[:-1]}
        candidates = []

        for direction in self.directions:
            neighbor = head + direction
            neighbor_key = self._vec_key(neighbor)

            if not self._in_bounds(neighbor):
                continue
            if neighbor_key in blocked:
                continue

            # Simulate one move
            if neighbor == apple:
                sim_snake = [neighbor] + [segment.copy() for segment in snake]
            else:
                sim_snake = [neighbor] + [segment.copy() for segment in snake[:-1]]

            # Candidate move must still allow tail reachability
            if self.astar(sim_snake, sim_snake[-1]) is None:
                continue

            # Prefer moves that keep us later in the cycle before the tail
            # and farther from the apple.
            cycle_progress = self.cycle_distance(neighbor, tail)
            apple_dist = abs(neighbor.x - apple.x) + abs(neighbor.y - apple.y)

            candidates.append((cycle_progress, apple_dist, neighbor))

        if not candidates:
            return None

        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return candidates[0][2]

    def get_next_move(self, snake, apple):
        if not snake:
            return None

        # 1. Shortest path to apple if safe
        path = self.astar(snake, apple)
        if path is not None and len(path) >= 2 and self.survival_check(snake, path):
            return path[1]

        # 2. Optional upgrade:
        # take a safe longer detour to avoid trapping yourself while growing
        long_move = self.longest_path_move(snake, apple)
        if long_move is not None:
            return long_move

        # 3. Safe shortcut along Hamiltonian order
        shortcut = self.perturb(snake, apple)
        if shortcut is not None:
            return shortcut

        # 4. Guaranteed safe fallback
        return self.next_in_cycle(snake[0])