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
Player = namedtuple('Player', 'position, dead')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

POISON = (200,0,0)
EADIBLE = (247, 149, 45)

BLOCK_SIZE = 6
SPEED = 20
MAX_FRAMES = 1000
class AIGame:
    
    def __init__(self, w=1400, h=750, seed=890, num_players=1):
        #display params
        self.width = w
        self.height = h
        self.w = 200
        self.h = 120
        self.board_start = 50
        self.tile = 20
        self.stats_w = 250

        # init display
        self.display = pygame.display.set_mode((self.width, self.height))
        self.game_board = pygame.surface.Surface((self.w*BLOCK_SIZE, self.h*BLOCK_SIZE)).convert()
        self.stats_board = pygame.surface.Surface((self.stats_w, self.height)).convert()
        pygame.display.set_caption('AIGame')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = Direction.RIGHT

        #snake
        self.agents = []
        self.num_agents = num_players
            
        self.score = 0
        self.record = 0
        self.stats = deque(maxlen=20)
        self.logs = deque(maxlen=8)

        self.hunger = [30 for _ in range(self.num_agents)]
        self.wait = False
        self.food_eadible = []
        self.food_poison = []
        self.seed = seed
        self._spawn_food_locations = []
        self.frame_iteration = 0
        self.world = generateWorld(self.w, self.h, seed)
        self._create_food()
        self.setup()

    def setup(self):
        for _ in range(self.num_agents):
            self.agents.append(Player(Point(int(self.w/2), int(self.h/2)), False))

    def set_stats(self, record):
        self.record = record
    
    def add_log(self, log):
        self.logs.append(log)

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.agents.clear()
        for _ in range(self.num_agents):
            self.agents.append(Player(Point(int(self.w/2), int(self.h/2)), False))

        self.hunger = [30 for _ in range(self.num_agents)]
        self.wait = False
        self.score = 0
        self.food_eadible = []
        self.food_poison = []
        self._create_food()
        self.frame_iteration = 0
    
    def _create_food(self):
        for i in range(int(self.w/self.tile)):
            for j in range(int(self.h/self.tile)):           
                for _ in range(10):
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

    def nearest_food(self, sight=1, pt=None):
        look = np.zeros((sight*2+1, sight*2+1))
        if pt is None:
            pt = self.player
        for i, x in enumerate(range(int(pt.x - sight), int(pt.x+sight))):
            for j, y in enumerate(range(int(pt.y-sight), int(pt.y + sight))):
                look[i,j] = ((x,y) in self.food_eadible)
        return look.flatten()    

    def get_terrain(self, pt=None):
        if pt is None:
            return
        (_, name) = self.world[(pt.x, pt.y)]
        return [name=="grass", name=="water", name=="forest", name=="water"]  

    def play_step(self, action, agent_index):
        self.frame_iteration += 1
        reward = 0
        player = self.agents[agent_index].position

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
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        
        
        (_, name) = self.world[(player.x, player.y)]
        if name == "swamp" and self.wait:
            pass
        else:
            # 2. move
            player = self._move(player, action) # update the player
            self.agents[agent_index] = Player(player, False)
        
        game_over, reason =  self.is_collision(player, agent_index)
        if game_over or self.frame_iteration > MAX_FRAMES:
            self.agents[agent_index] = Player(player, True)
            reward = -10
            return reward, game_over, reason, self.score

            
        # 4. eat food or just move
        if player in self.food_eadible:
            self.score += 1
            reward = 10 + (MAX_FRAMES-self.frame_iteration)//20
            if name == "swamp":
                self.hunger[agent_index] += 22
            else:
                self.hunger[agent_index] += 10
            self.food_eadible.remove(player)
            self._spawn_food_locations.append(Point(math.floor(player.x/self.tile), math.floor(player.y/self.tile)))
        
        self.stats.append(self.score)
        # 5. update ui and clock
        self._update_ui()
        if name == "swamp":
            self.hunger[agent_index] -= 1
        self.hunger[agent_index] -= 1
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, reason, self.score
    
    def is_collision(self, pt= None, index=0):
        # hits boundary
        reason = ""
        if pt is None:
           return   
        if pt.x > self.w or pt.x < 0 or pt.y > self.h - 1 or pt.y < 0:
            reason = "Walked into the electric fence!"
            return True, reason
        
        #starves
        hunger = self.hunger[index]
        if hunger <= 0:
            reason = "Starved to death!"
            return True, reason

        #eats poisoned food
        if pt in self.food_poison:
            reason = "Ate poison!"
            return True, reason
        #drowns
        (_, name) = self.world[(pt.x, pt.y)]
        if name == "water":
            reason = "Drowned!"
            return True, reason
        #gets killed by a predator
        elif name == "forest":
            x = random.randint(0, 100)
            if x < 3:
                reason = "Eaten by the predators"
                return True, reason
        
        return False, reason
    
    # Function to display text
    def _display_text(self, surface, text, font_size, position):
        font = pygame.font.Font(pygame.font.match_font("Arial"), font_size)
        text_surface = font.render(text, True, WHITE)
        surface.blit(text_surface, position)

    # Function to arrange strings in columns and rows
    def _display_array(self, surface, array, setoffx, setoffy):
        col_count = 3  # Number of columns
        row_count = (len(array) + col_count - 1) // col_count  # Calculate number of rows
        max_font_size = 15  # Maximum font size

        # Calculate font size based on array length
        font_size = min(self.stats_w // col_count, max_font_size)

        for i, text in enumerate(array):
            row = i // col_count
            col = i % col_count

            x = col * (self.stats_w // col_count) + setoffx
            y = row * (200 // row_count) + setoffy

            self._display_text(surface, text, font_size, (x, y))
        
    def _update_ui(self):
        self.display.fill(BLACK)
        self.drawBackground()
        self.drawBoard()
        self.display.blit(self.game_board, [self.board_start, self.board_start])
        self.draw_stats()
        self.display.blit(self.stats_board, [self.width-280, 0])
        pygame.display.update()
        pygame.display.flip()

    def drawBoard(self):
        
        for (pt, dead) in self.agents:
            (xp, yp) = (pt.x*BLOCK_SIZE,pt.y*BLOCK_SIZE)
            color = BLUE2 if not dead else BLACK
            pygame.draw.rect(self.game_board, color, pygame.Rect(xp, yp, BLOCK_SIZE, BLOCK_SIZE))

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
        font = pygame.font.Font(pygame.font.match_font("Arial"), 15)
        self.stats_board.fill(BLACK)
        self._display_text(self.stats_board, "Current best score: " + str(self.score), 26, (30, 30))
        pygame.draw.line(self.stats_board, (255, 255, 255, 0), (30, 100), ( 30,  255))
        pygame.draw.line(self.stats_board, (255, 255, 255, 0), (25, 250), ( 230,  250))
        if max(self.stats)> self.record:
            self.record = max(self.stats)
        text = font.render(str(self.record), True, WHITE)
        self.stats_board.blit(text, [10, 70])
        self.stats_board.blit(font.render(str(0), True, WHITE), [10, 250])
        for i in range(len(self.stats)-2):
            h1 = 250 - 150*((self.stats[i])/(self.record+1))
            h2 = 250 - 150*((self.stats[i+1])/(self.record+1))
            pygame.draw.line(self.stats_board, (255, 255, 255, 0), 
                             (30+i*10, h1), ( 30+(i+1)*10,  h2))
            
        for i, log in enumerate(self.logs):
            text = font.render("=> "+log, True, WHITE)
            self.stats_board.blit(text, [30, 300+25*i])
        
        self._display_text(self.stats_board, "Hunger", 20, (30, 510))
        self._display_array(self.stats_board, ["Agent" + str(i) + ":" + str(h) for i, h in enumerate(self.hunger)], 20, 550)

        
    def _move(self, player, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        self.direction = new_dir
        x = player.x
        y = player.y
        if self.direction == Direction.RIGHT:
            x += 1
        elif self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.DOWN:
            y += 1
        elif self.direction == Direction.UP:
            y -= 1
            
        return Point(x, y)

