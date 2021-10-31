import copy
import random
import gym
import math

from sympy.utilities.iterables import variations, multiset_permutations


class Tube:
    def __init__(self, balls: list = None, capacity: int = 4) -> None:
        """Initializes Tube

        Args:
            balls (list, optional): List with the balls. Defaults to [].
            capacity (int, optional): Capacity of a tube. Defaults to 4.
        """
        if balls is None:
            balls = []

        self.capacity = capacity
        self.balls = balls

    def is_empty(self):
        """Check if tube is empty

        Returns:
            boolean: True if empty, False otherwise
        """
        return len(self.balls) == 0

    def is_full(self):
        """Check if tube is full

        Returns:
            boolean: True if full, False otherwise
        """
        return len(self.balls) == self.capacity

    def get_ball(self):
        """Get the ball from the top of the tube

        Returns:
            int: Ball from the top
        """
        return self.balls[-1]

    def remove_ball(self):
        """Removes the top ball of a tube

        Returns:
            int: Removed ball
        """
        top_ball = self.get_ball()
        self.balls = self.balls[:-1]
        return top_ball

    def all_same_colored(self):
        """Check if all the balls in the tube have the same color

        Returns:
            boolean: True if the balls have the same color, False otherwise
        """
        for i in range(1, len(self.balls)):
            if self.balls[i] != self.balls[i - 1]:
                return False
        return True

    def put_ball(self, ball):
        """Put ball in tube

        Args:
            ball (int): New ball

        Returns:
            boolean: True if the ball was put in the tube, False if the tube was already full
        """
        if self.is_full():
            return False
        self.balls.append(ball)
        return True

    def print(self, place: int):
        """Print a tube

        Args:
            place (int): Height of the tube to print
        """
        try:
            print("|", self.balls[place], "|", end="")
        except:
            print("|   |", end="")

    def is_completed(self):
        """Check if tube is completed

        Returns:
            boolean: True if tube is completed, False otherwise
        """
        return self.all_same_colored() and self.is_full()

    def get_balls(self):
        """Returns the balls of the Tube

        Returns:
            list: balls of the tube
        """
        return self.balls

    def __eq__(self, other):
        if len(self.balls) != len(other.balls): return False
        for i in range(0, len(self.balls)):
            if self.balls[i] != other.balls[i]: return False
        return True

    def __hash__(self):
        hash_val = 0
        pos = 0
        for i in self.balls:
            hash_val += i * pos
            pos = pos + 1
        return hash_val * len(self.balls)


class Game(gym.Space):
    def __init__(self, tubes: list) -> None:
        self.tubes = []
        for tube in tubes:
            self.tubes.append(Tube(tube))
            self.num_of_colors = self.calculate_colors()
        
        self.n_tubes = len(self.tubes)
        self.n = self.calculate_possible_states()

    def calculate_possible_states(self):
        """Calculates the number of states from an initial configuration

        Returns:
            int: number of states
        """
        # All balls of the state
        balls = [x for x in range(1, self.num_of_colors + 1)] * 4

        # All possible tube configurations
        configurations = [x for x in variations([0, 1, 2, 3, 4], self.n_tubes, True) if sum(x) == 4 * self.num_of_colors]

        balls_permutations = multiset_permutations(balls)

        return len(self.generate_states(balls_permutations, configurations))
        #return len(balls_permutations) * len(configurations)


    def generate_states(self, perms, configurations):
        """Generates the states from a given configuration

        Returns:
            list: states
        """
        states = []
        for configuration in configurations:
            for perm in perms:
                tmp = []
                idx = 0
                for i in range(0, self.n_tubes):
                    if i == 0: 
                        tmp.append(list(perm[:configuration[i]]))
                    elif i == self.n_tubes - 1: 
                        tmp.append(list(perm[idx:]))
                    else: 
                        tmp.append(list(perm[idx: idx + configuration[i]]))
                    idx += configuration[i]
                states.append(tmp)
        return list(states)

    def calculate_colors(self):
        """Get number of colors in the game
        Returns:
            int: Number of different colors in the game
        """
        colors = set()
        for tube in self.tubes:
            balls = tube.get_balls()
            for ball in balls:
                colors.add(ball)
        return len(colors)

    def finished(self):
        """Checks if the game is finished

        Returns:
            boolean: True if the game is finished, False otherwise
        """
        completed_tubes = 0
        for tube in self.tubes:
            if tube.is_completed():
                completed_tubes += 1
        return completed_tubes == self.num_of_colors

    def move_ball(self, from_i: int, to_i: int):
        """Moves a ball from a tube to another

        Args:
            from_i (int): Index of the tube to remove the ball
            to_i (int): Index of the tube to put the ball

        Returns:
            boolean: True if the ball was moved, False otherwise
        """
        if self.tubes[from_i].is_empty() or self.tubes[to_i].is_full() or (
                not self.tubes[to_i].is_empty() and (self.tubes[from_i].get_ball() != self.tubes[to_i].get_ball())):
            return False
        else:
            return self.tubes[to_i].put_ball(self.tubes[from_i].remove_ball())

    def get_possible_actions(self):
        """Get current game state's possible actions

        Returns:
            list: List of possible actions
        """
        actions = []
        for action in range(0, pow(len(self.tubes), 2)):
            from_tube = action // self.n_tubes
            to_tube = action % self.n_tubes

            if from_tube == to_tube:
                continue

            if self.tubes[from_tube].is_empty() or self.tubes[to_tube].is_full():
                continue

            if self.tubes[to_tube].is_empty() or self.tubes[from_tube].get_ball() == self.tubes[to_tube].get_ball():
                actions.append(action)

        return actions

    def print(self):
        """Print a game state
        """
        for places in range(3, -1, -1):
            for tube in self.tubes:
                tube.print(places)
            print("")

        print(" --- " * len(self.tubes))

    
    def evaluate(self, valid: bool):
        """Evaluates a state

        IF INVALID STATE_: -1000 
        FOR EACH TUBE:
        - COUNT BALLS OF SAME COLOUR FROM BOTTOM TOP, 5*consecutive balls
        - COUNT NUMBER OF INCORRECTLY PLACED BALLS (not sure of this): -1*wrongly placed
        COMPLETED TUBE: +20

        Returns:
            int: reward
        """
        if not valid: return -1000
        if self.finished(): return 50
        reward = 0

        for tube in self.tubes:
            balls = tube.balls.copy()

            if len(balls) == 0: continue

            idx = next((i for i, v in enumerate(balls) if v != balls[0]), -1)
            if idx == -1:
                if len(balls) == 4:
                    reward += 5
                else:
                    reward += len(balls)
            else:
                balls = balls[idx:]
                reward -= len(balls)*10

        return reward
    

    def evaluate2(self, valid: bool):
        """Evaluates a state

        IF INVALID STATE: -5 
        IF FINISHED GAME: +20
        ELSE -1

        Returns:
            int: reward
        """
        if not valid: return -5
        if self.finished(): return 20
        return -1
    
    def evaluate3(self, valid: bool, to_tube):
        """Evaluates a state
        
        IF FINISHED GAME: +10
        IF FINISHED TUBE STATE: +1 
        ELSE -1

        Returns:
            int: reward
        """
        if self.finished(): return 10
        if self.tubes[to_tube].is_completed():
            return 1
        return -1

    def to_list(self):
        list = []
        for tube in self.tubes:
            list.append(tube.get_balls())
        return list

    def __eq__(self, other):
        for tube in self.tubes:
            if tube not in other.tubes:
                return False
        return True

    def __hash__(self):
        tubes = sorted(self.tubes, key=lambda x: x.__hash__())
        hash_val = 0
        for i in range(0, len(tubes)):
            hash_val += tubes[i].__hash__() * (i + 1)
        return hash_val
