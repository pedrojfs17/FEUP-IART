import gym
import tube
import numpy as np
import copy
from random import choice
from math import perm


# ACTION SPACE - MOVE BALL FROM X TO Y 
# e.g. for 2 tubes (simple), can move from 1 to 1, 1 to 2, 2 to 1 or 2 to 2 -> [1,4]
# (ACTION / num of tubes) - 1 = FROM TUBE 
# ACTION % num of tubes = TO TUBE

# OBSERVATION SPACE/STATE - THE PUZZLE ITSELF
# e.g. [[1],[1,1,1]] -> 

class Environment(gym.Env):
    states = {}
    i = 0

    def __init__(self, game):
        self.initial_state = copy.deepcopy(game)
        self.n_tubes = len(game)
        self.state = tube.Game(game)
        self.action_space = gym.spaces.Discrete(pow(len(game), 2))  # Combinacoes de N, 2 a 2 (N = numero de tubos)
        self.observation_space = tube.Game(game)  # puzzle
        self.put_dict(self.state)

    def step(self, action):
        state, reward, from_tube, to_tube = self.react(action)
        self.put_dict(state)
        done = state.finished()
        info = {'from_tube': from_tube, 'to_tube': to_tube}
        return state, reward, done, info

    def reset(self):
        return tube.Game(copy.deepcopy(self.initial_state))

    def put_dict(self, o):
        for state in self.states.keys():
            if state.__hash__() == o.__hash__(): return
        
        self.states[o.__hash__()] = self.i
        self.i += 1

    def render(self, mode='human', close=False):
        self.state.print()

    def get_index(self, o):
        return self.states[o.__hash__()]

    def get_action_space_sample(self):
        action_space = self.state.get_possible_actions()
        if len(action_space) == 0: return -1
        return choice(action_space)

    def react(self, action):
        from_tube = action // self.n_tubes
        to_tube = action % self.n_tubes

        new_state = copy.deepcopy(self.state)

        if from_tube == to_tube:
            valid = False
        else:
            valid = new_state.move_ball(from_tube, to_tube)

        reward = new_state.evaluate3(valid, to_tube)
        return new_state, reward, from_tube, to_tube
