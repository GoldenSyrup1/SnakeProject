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

    def cycle_distance(self, start, end):
        start_idx = self.cycle_index[self._vec_key(start)]
        end_idx = self.cycle_index[self._vec_key(end)]
        return (end_idx - start_idx) % len(self.cycle)

    def next_in_cycle(self, pos):
        idx = self.cycle_index[self._vec_key(pos)]
        return self.cycle[(idx + 1) % len(self.cycle)]

    def manhattan(self, a, b):
        return abs(a.x - b.x) + abs(a.y - b.y)

    def legal_neighbors(self, snake):
        head = snake[0]
        body = {self._vec_key(v) for v in snake[:-1]}

        neighbors = []
        for direction in self.directions:
            nxt = head + direction
            if not self._in_bounds(nxt):
                continue
            if self._vec_key(nxt) in body:
                continue
            neighbors.append(nxt)

        return neighbors

    def required_gap(self, snake_len):
        """
        Minimum safe free interval to preserve between head and tail.
        Bigger snake => more conservative.
        """
        board_cells = self.rows * self.cols
        fill_ratio = snake_len / board_cells

        if fill_ratio < 0.25:
            return 1
        if fill_ratio < 0.50:
            return 2
        if fill_ratio < 0.75:
            return 4
        return 6

    def is_safe_forward_move(self, snake, neighbor, apple):
        """
        Check whether moving to neighbor preserves Hamiltonian safety.

        We only allow moves that:
        - move forward along the cycle
        - do not jump past the tail
        - leave enough free interval after the move
        """
        head = snake[0]
        tail = snake[-1]

        free_interval = self.cycle_distance(head, tail)
        jump = self.cycle_distance(head, neighbor)

        if jump <= 0:
            return False

        if neighbor == apple:
            new_free_interval = free_interval - jump
        else:
            new_free_interval = free_interval - jump + 1

        return new_free_interval >= self.required_gap(len(snake))

    def safe_shortcuts(self, snake, apple):
        candidates = []

        for neighbor in self.legal_neighbors(snake):
            if not self.is_safe_forward_move(snake, neighbor, apple):
                continue

            head = snake[0]
            jump = self.cycle_distance(head, neighbor)
            remaining_to_apple = self.cycle_distance(neighbor, apple)

            tail = snake[-1]
            free_interval = self.cycle_distance(head, tail)
            if neighbor == apple:
                new_free_interval = free_interval - jump
            else:
                new_free_interval = free_interval - jump + 1

            candidates.append(
                {
                    "neighbor": neighbor,
                    "jump": jump,
                    "remaining_to_apple": remaining_to_apple,
                    "new_free_interval": new_free_interval,
                }
            )

        return candidates

    def best_shortcut(self, snake, apple):
        """
        Adaptive non-A* shortcut fallback.
        """
        head = snake[0]
        current_to_apple = self.cycle_distance(head, apple)

        shortcuts = self.safe_shortcuts(snake, apple)
        if not shortcuts:
            return None

        improving = [
            item for item in shortcuts
            if item["remaining_to_apple"] < current_to_apple
        ]

        if not improving:
            return None

        board_cells = self.rows * self.cols
        fill_ratio = len(snake) / board_cells

        if fill_ratio < 0.50:
            improving.sort(
                key=lambda item: (
                    item["remaining_to_apple"],
                    -item["jump"],
                    -item["new_free_interval"],
                )
            )
        elif fill_ratio < 0.80:
            improving.sort(
                key=lambda item: (
                    item["remaining_to_apple"],
                    -item["jump"],
                    item["new_free_interval"],
                )
            )
        else:
            improving.sort(
                key=lambda item: (
                    item["remaining_to_apple"],
                    item["jump"],
                    -item["new_free_interval"],
                )
            )

        return improving[0]["neighbor"]

    def _safe_astar_neighbors(self, snake, current, apple):
        """
        Generate only Hamiltonian-safe A* neighbors.
        """
        snake_head = snake[0]
        body = {self._vec_key(v) for v in snake[:-1]}

        neighbors = []
        for direction in self.directions:
            nxt = current + direction
            nxt_key = self._vec_key(nxt)

            if not self._in_bounds(nxt):
                continue
            if nxt_key in body and nxt_key != self._vec_key(snake_head):
                continue

            # We evaluate cycle safety relative to the current real snake head.
            # This is conservative: it only allows moves that are safe as direct next steps.
            # For the A* path, we further keep every visited node within the safe forward interval.
            if not self._node_in_safe_interval(snake, nxt):
                continue

            neighbors.append(nxt)

        return neighbors

    def _node_in_safe_interval(self, snake, node):
        """
        Restrict search nodes to the safe forward interval from head to tail.
        """
        head = snake[0]
        tail = snake[-1]
        dist_head_to_node = self.cycle_distance(head, node)
        dist_head_to_tail = self.cycle_distance(head, tail)

        reserve = self.required_gap(len(snake))
        return 0 < dist_head_to_node <= max(0, dist_head_to_tail - reserve)

    def safe_astar_to_apple(self, snake, apple):
        """
        A* inside the Hamiltonian-safe interval only.

        This does NOT allow arbitrary paths.
        It only searches among nodes that remain inside the safe interval
        between head and tail on the cycle.
        """
        head = snake[0]

        if not self._node_in_safe_interval(snake, apple) and apple != head:
            return None

        start_key = self._vec_key(head)
        goal_key = self._vec_key(apple)

        open_set = []
        heapq.heappush(open_set, (0, 0, start_key))

        came_from = {}
        g_score = {start_key: 0}
        visited = set()

        while open_set:
            _, g, current_key = heapq.heappop(open_set)

            if current_key in visited:
                continue
            visited.add(current_key)

            if current_key == goal_key:
                path = []
                node = current_key
                while node != start_key:
                    path.append(Vector2(node[0], node[1]))
                    node = came_from[node]
                path.append(Vector2(start_key[0], start_key[1]))
                path.reverse()
                return path

            current = Vector2(current_key[0], current_key[1])

            for neighbor in self._safe_astar_neighbors(snake, current, apple):
                neighbor_key = self._vec_key(neighbor)

                if neighbor_key in visited:
                    continue

                tentative_g = g + 1
                if neighbor_key not in g_score or tentative_g < g_score[neighbor_key]:
                    g_score[neighbor_key] = tentative_g
                    came_from[neighbor_key] = current_key
                    h = self.manhattan(neighbor, apple) // self.cell
                    heapq.heappush(
                        open_set,
                        (tentative_g + h, tentative_g, neighbor_key)
                    )

        return None

    def safe_astar_first_step(self, snake, apple):
        """
        Use safe A* only if every step in the returned path is forward-safe.
        This is the final guard before using it.
        """
        path = self.safe_astar_to_apple(snake, apple)
        if path is None or len(path) < 2:
            return None

        sim_snake = [segment.copy() for segment in snake]

        for step in path[1:]:
            if not self.is_safe_forward_move(sim_snake, step, apple):
                return None

            if step == apple:
                sim_snake = [step] + sim_snake
            else:
                sim_snake = [step] + sim_snake[:-1]

        return path[1]

    def get_next_move(self, snake, apple):
        if not snake:
            return None

        # 1. Safe constrained A*
        astar_move = self.safe_astar_first_step(snake, apple)
        if astar_move is not None:
            return astar_move

        # 2. Adaptive cycle shortcut fallback
        shortcut = self.best_shortcut(snake, apple)
        if shortcut is not None:
            return shortcut

        # 3. Guaranteed structured fallback
        return self.next_in_cycle(snake[0])