import random
import numpy as np
import pandas as pd
import collections
import torch
import torch.nn as nn
import torch.nn.functional as F

from game import Snake, Apple
from game import snake_hit_edge, snake_hit_apple, snake_hit_self

from settings import DEVICE


class Agent(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.reward = 0
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = params['learning_rate']
        self.epsilon = 1
        self.actual = []
        self.first_layer = params['first_layer_size']
        self.second_layer = params['second_layer_size']
        self.third_layer = params['third_layer_size']
        self.memory = collections.deque(maxlen=params['memory_size'])
        self.weights = params['weights_path']
        self.load_weights = params['load_weights']
        self.optimizer = None

        # Layers
        self.f1 = nn.Linear(12, self.first_layer)
        self.f2 = nn.Linear(self.first_layer, self.second_layer)
        self.f3 = nn.Linear(self.second_layer, self.third_layer)
        self.f4 = nn.Linear(self.third_layer, 3)
        # Weights
        if self.load_weights:
            self.model = self.load_state_dict(torch.load(self.weights))

    def to_device(self):
        return self.to(DEVICE)

    def forward(self, x):
        x = F.relu(self.f1(x))
        x = F.relu(self.f2(x))
        x = F.relu(self.f3(x))
        x = F.softmax(self.f4(x), dim=-1)
        return x

    def set_reward(self, snake: Snake, apple: Apple, head_apple_distance_new_x, head_apple_distance_old_x,
                   head_apple_distance_new_y, head_apple_distance_old_y):
        """
        Return the reward.
        The reward is:
            -10 when Snake crashes.
            +10 when Snake eats food
            0 otherwise
        """
        self.reward = 0
        if snake_hit_self(snake) or snake_hit_edge(snake):
            self.reward = -20
            return self.reward
        if snake_hit_apple(snake, apple):
            self.reward = 10
        if head_apple_distance_new_x < head_apple_distance_old_x or\
                head_apple_distance_new_y < head_apple_distance_old_y:
            self.reward = 1
        elif head_apple_distance_new_x > head_apple_distance_old_x or\
                head_apple_distance_new_y > head_apple_distance_old_y:
            self.reward = -1
        return self.reward

    def remember(self, state, action, reward, next_state, done):
        """
        Store the <state, action, reward, next_state, is_done> tuple in a
        memory buffer for replay memory.
        """
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory, batch_size):
        """
        Replay memory.
        """
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            self.train()
            torch.set_grad_enabled(True)  # sets gradient calculation to on.
            target = reward
            next_state_tensor = torch.tensor(np.expand_dims(next_state, 0), dtype=torch.float32).to(DEVICE)
            state_tensor = torch.tensor(np.expand_dims(state, 0), dtype=torch.float32, requires_grad=True).to(DEVICE)
            if not done:
                target = reward + self.gamma * torch.max(self.forward(next_state_tensor)[0])
            output = self.forward(state_tensor)
            target_f = output.clone()
            target_f[0][np.argmax(action)] = target
            target_f.detach()
            self.optimizer.zero_grad()
            loss = F.mse_loss(output, target_f)
            loss.backward()
            self.optimizer.step()

    def train_short_memory(self, state, action, reward, next_state, done):
        """
        Train the DQN agent on the <state, action, reward, next_state, is_done>
        tuple at the current timestep.
        """
        self.train()
        torch.set_grad_enabled(True)
        target = reward
        next_state_tensor = torch.tensor(next_state.reshape((1, 12)), dtype=torch.float32).to(DEVICE)
        state_tensor = torch.tensor(state.reshape((1, 12)), dtype=torch.float32, requires_grad=True).to(DEVICE)
        if not done:
            target = reward + self.gamma * torch.max(self.forward(next_state_tensor[0]))
        output = self.forward(state_tensor)
        target_f = output.clone()
        target_f[0][np.argmax(action)] = target
        target_f.detach()
        self.optimizer.zero_grad()
        loss = F.mse_loss(output, target_f)
        loss.backward()
        self.optimizer.step()
