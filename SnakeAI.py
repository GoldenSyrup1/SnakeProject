import random
from pygame.math import Vector2
import matplotlib.pyplot as plt

class SnakeEnv:
    def __init__(self, width=1000, height=500, cell=25):
        self.width = width
        self.height = height
        self.cell = cell
        self.reset()

    def reset(self):
        self.start_x = self.width // 2
        self.start_y = self.height // 2

        self.snake = [Vector2(self.start_x, self.start_y)]
        self.direction = Vector2(self.cell, 0)

        self.apple = self.spawn_apple()
        self.done = False
        self.score = 0

        return self.get_state()

    def spawn_apple(self):
        while True:
            pos = Vector2(
                random.randrange(0, self.width, self.cell),
                random.randrange(0, self.height, self.cell)
            )
            if pos not in self.snake:
                return pos

    def dist_to_body(self):
        head = self.snake[0]
        return min((head - s).length() for s in self.snake[1:]) if len(self.snake) > 1 else 999
    def step(self, action):
        # actions: 0 = left, 1 = straight, 2 = right
        if action == 0:
            self.direction = self.direction.rotate(-90)
        elif action == 2:
            self.direction = self.direction.rotate(90)

        new_head = self.snake[0] + self.direction

        reward = -0.1
        self.done = False



        prev_dist = self.dist_to_body()
        new_dist = self.dist_to_body()
        if new_dist < prev_dist:
            reward -= 0.2
        head = self.snake[0]
        margin = self.cell * 2

        if (
                head.x < margin or head.x > self.width - margin or
                head.y < margin or head.y > self.height - margin
        ):
            reward -= 0.2

        # collision
        if (
            new_head.x < 0 or new_head.x >= self.width or
            new_head.y < 0 or new_head.y >= self.height or
            new_head in self.snake
        ):
            reward = -10
            self.done = True
            return self.get_state(), reward, self.done

        self.snake.insert(0, new_head)

        if new_head == self.apple:
            reward = 10
            self.score += 1
            self.apple = self.spawn_apple()
        else:
            self.snake.pop()

        return self.get_state(), reward, self.done

    def get_state(self):
        head = self.snake[0]

        def danger(dir_vec):
            pos = head + dir_vec
            return (
                pos.x < 0 or pos.x >= self.width or
                pos.y < 0 or pos.y >= self.height or
                pos in self.snake
            )

        left = self.direction.rotate(-90)
        right = self.direction.rotate(90)
        tail = self.snake[-1]

        tail_left = tail.x < head.x
        tail_right = tail.x > head.x
        tail_up = tail.y < head.y
        tail_down = tail.y > head.y

        state = (
            danger(self.direction),
            danger(left),
            danger(right),

            self.apple.x < head.x,
            self.apple.x > head.x,
            self.apple.y < head.y,
            self.apple.y > head.y,

            self.direction.x < 0,
            self.direction.x > 0,
            self.direction.y < 0,
            self.direction.y > 0,
            tail_left,
            tail_right,
            tail_up,
            tail_down

        )

        return state

q_table = {}

def get_q(snake_state):
    return q_table.setdefault(snake_state, [0, 0, 0])

alpha = 0.1
gamma = 0.9
env = SnakeEnv()
episodes = 500000
scores = []

for episode in range(episodes):
    state = env.reset()
    done = False

    epsilon = max(0.01, 1 - episode / 600)

    while not done:
        if random.random() < epsilon:
            action = random.randint(0, 2)
        else:
            action = get_q(state).index(max(get_q(state)))

        next_state, reward, done = env.step(action)

        q = get_q(state)
        q[action] += alpha * (reward + gamma * max(get_q(next_state)) - q[action])

        state = next_state

    scores.append(env.score)

    if episode % 250 == 0:
        print(f"Episode {episode} | Score: {env.score}")


def moving_avg(data, window=50):
    return [sum(data[i-window:i]) / window for i in range(window, len(data))]

plt.plot(moving_avg(scores))
plt.xlabel("Episode")
plt.ylabel("Average Score")
plt.title("Snake RL Training Progress")
plt.show()


