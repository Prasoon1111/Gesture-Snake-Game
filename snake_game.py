from enum import Enum
import random

import pygame


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class SnakeGame:
    def __init__(self, width: int = 600, height: int = 600):
        """Initialize the snake game with a simple, readable UI."""
        self.width = width
        self.height = height
        self.grid_size = 20
        self.grid_width = width // self.grid_size
        self.grid_height = height // self.grid_size

        self.BACKGROUND = (14, 18, 16)
        self.GRID = (28, 38, 34)
        self.TEXT = (235, 240, 235)
        self.SNAKE_HEAD = (122, 220, 122)
        self.SNAKE_BODY = (78, 170, 98)
        self.FOOD = (255, 110, 90)

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Gesture Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 24)

        # Keep speed easy to tweak and intentionally slow.
        self.snake_speed = 4
        self.update_interval = 1.0 / self.snake_speed
        self.reset_game()

    def reset_game(self):
        """Reset the game state."""
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self.spawn_fruit()

    def spawn_fruit(self):
        """Spawn fruit only on free cells."""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake:
                self.fruit = (x, y)
                return

    def change_direction(self, new_direction: str):
        """Queue a safe direction change and block instant reversal."""
        if self.game_over:
            return

        direction_map = {
            "UP": Direction.UP,
            "DOWN": Direction.DOWN,
            "LEFT": Direction.LEFT,
            "RIGHT": Direction.RIGHT,
        }
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        if new_direction not in direction_map:
            return

        new_dir = direction_map[new_direction]
        if new_dir != opposite[self.direction] and new_dir != opposite[self.next_direction]:
            self.next_direction = new_dir

    def update(self):
        """Move the snake at a controlled, slow interval."""
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= self.grid_width
            or new_head[1] < 0
            or new_head[1] >= self.grid_height
            or new_head in self.snake[:-1]
        ):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.fruit:
            self.score += 10
            self.spawn_fruit()
        else:
            self.snake.pop()

    def draw_grid(self):
        """Draw a subtle grid to support the clean background."""
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(self.screen, self.GRID, (x, 0), (x, self.height))
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(self.screen, self.GRID, (0, y), (self.width, y))

    def draw_snake(self):
        """Draw the snake with simple rounded segments."""
        for index, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                x * self.grid_size + 2,
                y * self.grid_size + 2,
                self.grid_size - 4,
                self.grid_size - 4,
            )
            color = self.SNAKE_HEAD if index == 0 else self.SNAKE_BODY
            pygame.draw.rect(self.screen, color, rect, border_radius=6)

    def draw_fruit(self):
        """Draw the food as a small solid circle."""
        center = (
            self.fruit[0] * self.grid_size + self.grid_size // 2,
            self.fruit[1] * self.grid_size + self.grid_size // 2,
        )
        pygame.draw.circle(self.screen, self.FOOD, center, self.grid_size // 2 - 4)

    def draw_ui(self):
        """Keep the HUD minimal and readable."""
        score_text = self.font.render(f"Score: {self.score}", True, self.TEXT)
        info_text = self.small_font.render("Move finger in direction zones", True, self.TEXT)
        self.screen.blit(score_text, (14, 12))
        self.screen.blit(info_text, (14, 44))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("Game Over", True, self.TEXT)
            restart_text = self.small_font.render("Press R to restart", True, self.TEXT)
            self.screen.blit(game_over_text, game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 10)))
            self.screen.blit(restart_text, restart_text.get_rect(center=(self.width // 2, self.height // 2 + 22)))

    def draw(self):
        """Render the full game frame."""
        self.screen.fill(self.BACKGROUND)
        self.draw_grid()
        self.draw_snake()
        self.draw_fruit()
        self.draw_ui()
        pygame.display.flip()

    def get_update_interval(self) -> float:
        """Expose the slow movement interval for the main loop."""
        return self.update_interval

    def quit(self):
        """Quit pygame cleanly."""
        pygame.quit()
