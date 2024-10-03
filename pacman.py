import pygame
import random
import sys
from collections import deque
import numpy as np

# Constants
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 30
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
FPS = 8  # Reduced FPS for slower game

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)  # Синій колір

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]


# Maze generation using recursive backtracking
def generate_maze(width, height, level=1):
    maze = np.zeros((height, width), dtype=int)

    for i in range(1, height - 1, 2):
        for j in range(1, width - 1, 2):
            maze[i, j] = 1  # Create rooms

    stack = [(1, 1)]
    visited = set()

    while stack:
        current = stack[-1]
        visited.add(current)
        neighbors = get_unvisited_neighbors(current, maze, visited)

        if neighbors:
            next_cell = random.choice(neighbors)
            remove_wall(maze, current, next_cell)
            stack.append(next_cell)
        else:
            stack.pop()

    add_difficulty(maze, level)

    return maze


def get_unvisited_neighbors(cell, maze, visited):
    neighbors = []
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
    for d in directions:
        neighbor = (cell[0] + d[0], cell[1] + d[1])
        if 0 <= neighbor[0] < maze.shape[0] and 0 <= neighbor[1] < maze.shape[1]:
            if neighbor not in visited and maze[neighbor] == 1:
                neighbors.append(neighbor)
    return neighbors


def remove_wall(maze, cell1, cell2):
    x1, y1 = cell1
    x2, y2 = cell2
    maze[(x1 + x2) // 2, (y1 + y2) // 2] = 1


def add_difficulty(maze, level):
    height, width = maze.shape

    # Increased number of walls to create a more difficult maze at the beginning
    if level == 1:
        num_extra_paths = width * 20  # More walls for level 1
    elif level <= 3:
        num_extra_paths = width * 15
    elif level <= 5:
        num_extra_paths = width * 10
    else:
        num_extra_paths = width

    for _ in range(num_extra_paths):
        x = random.randint(1, height - 2)
        y = random.randint(1, width - 2)
        if maze[x, y] == 0:
            maze[x, y] = 1


# BFS algorithm for ghost movement
def bfs(maze, start, goal):
    queue = deque([start])
    visited = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for direction in DIRECTIONS:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if (0 <= neighbor[0] < len(maze[0]) and 0 <= neighbor[1] < len(maze) and
                    neighbor not in visited and maze[neighbor[1]][neighbor[0]] == 1):
                queue.append(neighbor)
                visited[neighbor] = current

    path = []
    while current:
        path.append(current)
        current = visited[current]
    return path[::-1]


# Coin class
class Coin:
    def __init__(self, maze):
        self.position = self.generate_random_position(maze)

    def generate_random_position(self, maze):
        while True:
            x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
            if maze[y][x] == 1:  # Ensure the position is free
                return (x, y)

    def draw(self, screen):
        screen.blit(nom_dot, (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE))


# Pacman class
class Pacman:
    def __init__(self, initial_position):
        self.position = initial_position
        self.direction = RIGHT  # Initial direction
        self.score = 0  # Track score

    def move(self, maze):
        new_pos = (self.position[0] + self.direction[0], self.position[1] + self.direction[1])
        if maze[new_pos[1]][new_pos[0]] == 1:  # Check for wall
            self.position = new_pos  # Update position if move is valid
            return True
        else:
            return False  # Stop movement without changing position

    def eat_coin(self, small_coins):
        if self.position in small_coins:
            small_coins.remove(self.position)
            self.score += 1

    def draw(self, screen):
        if self.direction == UP:
            screen.blit(pacman_up, (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE))
        elif self.direction == DOWN:
            screen.blit(pacman_down, (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE))
        elif self.direction == LEFT:
            screen.blit(pacman_left, (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE))
        elif self.direction == RIGHT:
            screen.blit(pacman_right, (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE))


# Ghost class
class Ghost:
    def __init__(self, initial_position, image):
        self.position = initial_position
        self.image = image  # Set the ghost's image
        self.move_counter = 0  # Counter to control movement speed

    def move_towards(self, target, maze):
        # Move every four frames to make ghosts slower
        self.move_counter += 1
        if self.move_counter % 4 == 0:  # Adjust this value for speed
            path = bfs(maze, self.position, target)
            if len(path) > 1:  # Move towards the target
                self.position = path[1]  # Move to next position in path

    def draw(self, screen):
        screen.blit(self.image, (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE))


# Main game class
class PacmanGame:
    def __init__(self, level):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        self.running = True

        # Load images
        global pacman_down, pacman_up, pacman_left, pacman_right, green_ghost, orange_ghost, red_ghost, nom_dot
        pacman_down = pygame.image.load("pacmandown.png").convert_alpha()
        pacman_up = pygame.image.load("pacmanup.png").convert_alpha()
        pacman_left = pygame.image.load("pacmanleft.png").convert_alpha()
        pacman_right = pygame.image.load("pacmanright.png").convert_alpha()

        green_ghost = pygame.image.load("GreenGhost.png").convert_alpha()
        orange_ghost = pygame.image.load("OrangeGhost.png").convert_alpha()
        red_ghost = pygame.image.load("RedGhost.png").convert_alpha()

        nom_dot = pygame.image.load("nomdot.png").convert_alpha()

        self.level = level
        self.maze = generate_maze(COLS, ROWS, level)  # Generate maze with difficulty level
        self.pacman = Pacman((COLS // 2, ROWS // 2))  # Start Pacman at the center of the maze
        self.ghosts = [Ghost((COLS - 2, ROWS - 2), green_ghost),
                       Ghost((COLS - 2, 1), orange_ghost),
                       Ghost((1, ROWS - 2), red_ghost)]
        self.coin = Coin(self.maze)  # Initialize coin
        self.small_coins = [(x, y) for y in range(ROWS) for x in range(COLS) if self.maze[y][x] == 1]  # Small coins in free cells

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.pacman.direction = UP
            elif keys[pygame.K_DOWN]:
                self.pacman.direction = DOWN
            elif keys[pygame.K_LEFT]:
                self.pacman.direction = LEFT
            elif keys[pygame.K_RIGHT]:
                self.pacman.direction = RIGHT

            if self.pacman.move(self.maze):  # Pass the maze to the move method
                            self.pacman.eat_coin(self.small_coins)  # Check for small coins

            for ghost in self.ghosts:
                ghost.move_towards(self.pacman.position, self.maze)

            # Check for collision
            for ghost in self.ghosts:
                if ghost.position == self.pacman.position:
                    print("Game Over!")
                    self.running = False

            # Check if Pacman has eaten the main coin
            if self.pacman.position == self.coin.position:
                self.level += 1
                print(f"Level passed! next... level {self.level}")
                self.maze = generate_maze(COLS, ROWS, self.level)  # Regenerate maze
                self.pacman.position = (COLS // 2, ROWS // 2)  # Reset Pacman's position
                self.small_coins = [(x, y) for y in range(ROWS) for x in range(COLS) if self.maze[y][x] == 1]  # Regenerate small coins
                self.coin = Coin(self.maze)  # Regenerate main coin

            self.screen.fill(BLACK)

            # Draw maze
            for y in range(ROWS):
                for x in range(COLS):
                    if self.maze[y][x] == 0:
                        pygame.draw.rect(self.screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Draw Pacman
            self.pacman.draw(self.screen)

            # Draw ghosts
            for ghost in self.ghosts:
                ghost.draw(self.screen)

            # Draw main coin
            self.coin.draw(self.screen)

            # Draw small coins
            for small_coin in self.small_coins:
                pygame.draw.circle(self.screen, (255, 255, 225), (int(small_coin[0] * CELL_SIZE + CELL_SIZE // 2),
                                                                int(small_coin[1] * CELL_SIZE + CELL_SIZE // 2)),
                                CELL_SIZE // 6)  # Зменшений розмір

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# Start the game
if __name__ == "__main__":
    game = PacmanGame(level=1)
    game.run() 