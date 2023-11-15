import pygame
import random
from enum import Enum
from collections import namedtuple
from world_generator import generateWorld
import pickle
import math
import numpy as np
from collections import deque

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

POISON = (200,0,0)
EADIBLE = (247, 149, 45)

BLOCK_SIZE = 6
SPEED = 5

class HumanGame:
    
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
        self.game_board = pygame.surface.Surface((self.w*BLOCK_SIZE, self.h*BLOCK_SIZE)).convert()
        self.stats_board = pygame.surface.Surface((250, h)).convert()
        pygame.display.set_caption('HumanGame')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = Direction.RIGHT

        #snake
        self.head = Point(int(self.w/2), int(self.h/2))
        self.player = [self.head]
            
        self.score = 0
        self.stats = deque(maxlen=20)

        self.hunger = 30
        self.wait = False
        self.food_eadible = []
        self.food_poison = []
        self.seed = seed
        self._spawn_food_locations = []
        self.world = generateWorld(self.w, self.h, seed)
        self._create_food()
    
    def _create_food(self):
        for i in range(int(self.w/self.tile)):
            for j in range(int(self.h/self.tile)):           
                for _ in range(5):
                    self._place_food(i, j, self.food_eadible)
                for _ in range(2):
                    self._place_food(i, j, self.food_poison)


    def _place_food(self, w, h, food_array):
        x = random.randint(w*self.tile, (w+1)*self.tile-1)
        y = random.randint(h*self.tile, (h+1)*self.tile-1)
        (_, name) = self.world[(x, y)]
        if name == 'water': #no food in water
            return
        elif name == 'swamp': #more food on swamps
            n = random.randint(0, 100)
            if n < 7:
                self._place_food(w,h,food_array)
        elif name == 'forest': #much more food in the forest
            n = random.randint(0, 100)
            if n < 15:
                self._place_food(w,h,food_array)
        food_array.append(Point(x, y))


    def play_step(self):
        # 1. collect user input
        self.wait = not(self.wait)
        if self.clock.get_time() % 40 == 0:
            for spawn in self._spawn_food_locations:
                self._place_food(spawn.x, spawn.y, self.food_eadible)
            self._spawn_food_locations.clear()


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
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        
        
        (_, name) = self.world[(self.head.x, self.head.y)]
        if name == "swamp" and self.wait:
            pass
        else:
            # 2. move
            self._move(self.direction) # update the head
            self.player.insert(0, self.head)
            self.player.pop()
        
        # 3. check if game over
        '''if self._is_collision():
            return True, self.score'''
            
        # 4. eat food or just move
        if self.head in self.food_eadible:
            self.score += 1
            self.hunger += 7
            self.food_eadible.remove(self.head)
            self._spawn_food_locations.append(Point(math.floor(self.head.x/self.tile), math.floor(self.head.y/self.tile)))
        
        self.stats.append(self.score)
        # 5. update ui and clock
        self._update_ui()
        self.hunger -= 1
        self.clock.tick(SPEED)
        # 6. return game over and score
        return False, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w or self.head.x < 0 or self.head.y > self.h - 1 or self.head.y < 0:
            print("Walked into the electric fence!")
            return True
        
        if self.hunger <= 0:
            print("Starved to death!")
            return True

        #eats poisoned food
        if self.head in self.food_poison:
            print("Ate poison!")
            return True
        #drowns
        (_, name) = self.world[(self.head.x, self.head.y)]
        if name == "water":
            print("Drowned!")
            return True
        #gets killed by a predator
        elif name == "forest":
            x = random.randint(0, 100)
            if x < 3:
                print("Eaten by the predators")
                return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        self.drawBackground()
        self.drawBoard()
        self.display.blit(self.game_board, [self.board_start, self.board_start])

        self.draw_stats()
        self.display.blit(self.stats_board, [self.width-260, 0])
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [self.width-200, 0])
        text2 = font.render("Hunger: " + str(self.hunger), True, WHITE)
        self.display.blit(text2, [self.width-200, 40])
        pygame.display.update()
        pygame.display.flip()

    def drawBoard(self):
        
        for pt in self.player:
            (xp, yp) = (pt.x*BLOCK_SIZE,pt.y*BLOCK_SIZE)
            pygame.draw.rect(self.game_board, BLUE1, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))

        for food in self.food_eadible:    
            (xp, yp) = (food.x*BLOCK_SIZE,food.y*BLOCK_SIZE)
            pygame.draw.rect(self.game_board, EADIBLE, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))

        for food in self.food_poison:    
            (xp, yp) = (food.x*BLOCK_SIZE,food.y*BLOCK_SIZE)
            pygame.draw.rect(self.game_board, POISON, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))

    def drawBackground(self):
        for (x, y), ((r,g,b,_), _) in self.world.items():
                pygame.draw.rect(self.game_board, (r*255,g*255,b*255), pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        
        for x in range(0,   self.w*BLOCK_SIZE, BLOCK_SIZE):
            pygame.draw.line(self.game_board, (255, 255, 255, 0), (x, 0), ( x,  self.h*BLOCK_SIZE))
        for y in range(0,  self.h*BLOCK_SIZE, BLOCK_SIZE):
            pygame.draw.line(self.game_board, (255, 255, 255, 20), (0, y), ( self.w*BLOCK_SIZE, y))   

    def draw_stats(self):
        self.stats_board.fill(BLACK)
        pygame.draw.line(self.stats_board, (255, 255, 255, 0), (30, 100), ( 30,  255))
        pygame.draw.line(self.stats_board, (255, 255, 255, 0), (25, 250), ( 230,  250))
        text = font.render(str(max(self.stats)), True, WHITE)
        self.stats_board.blit(text, [10, 70])
        self.stats_board.blit(font.render(str(0), True, WHITE), [10, 250])
        for i in range(len(self.stats)-2):
            h1 = 250 - 150*((self.stats[i]+1)/(max(self.stats)+1))
            h2 = 250 - 150*((self.stats[i+1]+1)/(max(self.stats)+1))
            pygame.draw.line(self.stats_board, (255, 255, 255, 0), 
                             (30+i*10, h1), ( 30+(i+1)*10,  h2))


        
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

