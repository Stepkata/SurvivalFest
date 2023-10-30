import pygame
import random
from enum import Enum
from collections import namedtuple
from world_generator import generateWorld
import pickle
import math
import numpy as np

pygame.init()
#font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

Food = namedtuple('Food', 'x, y, eadible, color')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

POSON = (200,0,0)
EADIBLE = (247, 149, 45)

BLOCK_SIZE = 6
SPEED = 5

class Game:
    
    def __init__(self, w=1400, h=750, seed=890):
        #display params
        self.width = w
        self.height = h
        self.w = 200
        self.h = 120
        self.board_start = 50
        self.tile = 20

        # init display
        self.display = pygame.display.set_mode((self.width, self.height))
        #self.game_board = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Game')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = Direction.RIGHT

        #snake
        self.head = Point(int(self.w/2), int(self.h/2))
        self.snake = [self.head, 
                      Point(self.head.x-1, self.head.y),
                      Point(self.head.x-2, self.head.y)]
        
        
        self.score = 0
        self.food_eadible = []
        self.food_poison = []
        self.food = np.empty(int(self.w/self.tile)*int(self.h/self.tile))
        self.seed = seed
        self.world = generateWorld(self.w, self.h, seed)
        self._create_food()

    def _board_point(self, x):
        return self.board_start + x*BLOCK_SIZE

    def _board_points(self, x, y):
        return (self._board_point(x), self._board_point(y))
    
    def _create_food(self):
        for i in range(int(self.w/self.tile)):
            for j in range(int(self.h/self.tile)):           
                for _ in range(5):
                    self._place_food(i, j, self.food_eadible)
                for _ in range(5):
                    self._place_food(i, j, self.food_poison)
        
    def _place_food(self, w, h, food_array):
        x = random.randint(w*self.tile, (w+1)*self.tile-1)
        y = random.randint(h*self.tile, (h+1)*self.tile-1)
        (_, name) = self.world[(x, y)]
        if name == 'water':
            return
        food_array.append(Point(x, y))
        if food_array in self.snake:
            self._place_food()

    def _spawn_food(self, food_array):
        for food in food_array:
                n = random.randint(0, 100)
                if n<4:
                    self._place_food(math.floor(food.x/self.tile), math.floor(food.y/self.tile), food_array)

    def play_step(self):
        # 1. collect user input
        SPEED = 5
        if self.clock.get_time() % 20 == 0:
            self._spawn_food(self.food_eadible)
            self._spawn_food(self.food_poison)


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
        
        
        (_, name) = self.world[(self.head.x, self.head.y)]
        if name == "swamp":
            SPEED -= 2

        # 2. move
        self._move(self.direction) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        game_over = self._is_collision()
        if game_over:
            return game_over, self.score
            
        # 4. eat food or just move
        if self.head in self.food_eadible:
            self.score += 1
            self.food_eadible.remove(self.head)
            self._place_food(math.floor(self.head.x/self.tile), math.floor(self.head.y/self.tile), self.food_eadible)
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w or self.head.x < 0 or self.head.y > self.h - 1 or self.head.y < 0:
            return True
        # hits itself
        if self.head in self.snake[1:]:
            x = random.randint(0, 10)
            if x < 7:
                return True
        #eats poisoned food
        if self.head in self.food_poison:
            return True
        #drowns
        (_, name) = self.world[(self.head.x, self.head.y)]
        if name == "water":
            return True
        #gets killed by a predator
        elif name == "forest":
            x = random.randint(0, 100)
            if x < 3:
                return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        self.drawBoard()
        
        for pt in self.snake:
            (xp, yp) = self._board_points(pt.x,pt.y)
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))

        for food in self.food_eadible:    
            (xp, yp) = self._board_points(food.x,food.y)
            pygame.draw.rect(self.display, EADIBLE, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))

        for food in self.food_poison:    
            (xp, yp) = self._board_points(food.x,food.y)
            pygame.draw.rect(self.display, POSON, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def drawBoard(self):
        pygame.draw.rect(self.display, (140, 140, 140), pygame.Rect(self.board_start-BLOCK_SIZE, self.board_start-BLOCK_SIZE, 
                                                                    (self.w+2)*BLOCK_SIZE, (self.h+2)*BLOCK_SIZE))
        for (x, y), ((r,g,b,_), _) in self.world.items():
                (xp, yp) = self._board_points(x,y)
                pygame.draw.rect(self.display, (r*255,g*255,b*255), pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))
        
        for x in range(self.board_start,   self._board_point(self.w), BLOCK_SIZE):
            pygame.draw.line(self.display, (255, 255, 255, 0), (x, self.board_start), ( x,  self._board_point(self.h)))
        for y in range(self.board_start,   self._board_point(self.h), BLOCK_SIZE):
            pygame.draw.line(self.display, (255, 255, 255, 20), (self.board_start, y), (  self._board_point(self.w), y))

        
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.UP:
            y -= 1
            
        self.head = Point(x, y)


            

if __name__ == '__main__':
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h

    game = Game(screen_width, screen_height)
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)

        
    pygame.quit()