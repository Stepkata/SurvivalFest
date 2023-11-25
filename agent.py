import torch
import random
import numpy as np
from collections import deque
from game import Direction, Point
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self, i=0):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.sight = 4
        self.inputs = 11 + pow(self.sight*2+1, 2)
        self.hidden = 256
        self.outputs = 3
        self.model = Linear_QNet(self.inputs, self.hidden, self.outputs)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

        self.index = i
        self.plot_scores = []
        self.plot_mean_scores = []
        self.total_score = 0
        self.record = 0


    def get_state(self, game):
        head = game.agents[self.index]
        point_l = Point(head.x - 1, head.y)
        point_r = Point(head.x + 1, head.y)
        point_u = Point(head.x, head.y - 1)
        point_d = Point(head.x, head.y + 1)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        col_r, _ = game.is_collision(point_r, self.index)
        col_l, _ = game.is_collision(point_l, self.index)
        col_u, _ = game.is_collision(point_u, self.index)
        col_d, _ = game.is_collision(point_d, self.index)

        state = [
            # Danger straight
            (dir_r and col_r) or 
            (dir_l and col_l) or 
            (dir_u and col_u) or 
            (dir_d and col_d),

            # Danger right
            (dir_u and col_r) or 
            (dir_d and col_l) or 
            (dir_l and col_u) or 
            (dir_r and col_d),

            # Danger left
            (dir_d and col_r) or 
            (dir_u and col_l) or 
            (dir_r and col_u) or 
            (dir_l and col_d),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            ]
        look = game.nearest_food(self.sight, head)
        state.extend(look)
        terrain = game.get_terrain(head)
        state.extend(terrain)
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

