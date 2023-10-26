import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
#font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 5
SPEED = 5

class Game:
    
    def __init__(self, w=1400, h=750):
        self.w = w
        self.h = h
        self.board_start = 50
        self.bw = 200*BLOCK_SIZE
        self.bh = 100*BLOCK_SIZE

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = []
        self.rivers = []
        self.mountains = []
        self._create_food()

    def _create_food(self):
        for _ in range(30):
            self._place_food()
        
    def _place_food(self):
        x = random.randint(self.board_start//BLOCK_SIZE, (self.bw+self.board_start-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(self.board_start//BLOCK_SIZE, (self.bh+self.board_start-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food.append(Point(x, y))
        if self.food in self.snake:
            self._place_food()

    def _create_rivers(self):
        pass
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        # 2. move
        self._move(self.direction) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if self.head in self.food:
            self.score += 1
            self.food.remove(self.head)
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.bw+2*self.board_start - BLOCK_SIZE or self.board_start < 0 or self.head.y > self.bh+2*self.board_start - BLOCK_SIZE or self.head.y < self.board_start:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        self.drawBoard()
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        for food in self.food:    
            pygame.draw.rect(self.display, RED, pygame.Rect(food.x, food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def drawBoard(self):
        pygame.draw.rect(self.display, (0,255,0), pygame.Rect(self.board_start, self.board_start, self.bw+self.board_start, self.bh+self.board_start))
        for x in range(self.board_start,  self.bw+2*self.board_start, BLOCK_SIZE):
            pygame.draw.line(self.display, WHITE, (x, self.board_start), (x, self.bh+2*self.board_start))
        for y in range(self.board_start,  self.bh+2*self.board_start, BLOCK_SIZE):
            pygame.draw.line(self.display, WHITE, (self.board_start, y), (self.bw+2*self.board_start, y))

        
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
            

if __name__ == '__main__':
    game = Game()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)

        
    pygame.quit()