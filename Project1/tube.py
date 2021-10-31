import copy

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

    def get_balls(self):
        """Get balls from tube

        Returns:
            list: Balls from the tube
        """
        return self.balls

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

    def __eq__(self, other):
        """Checks if two tubes are equa;

        Args:
            other (Tube): Tube to compare

        Returns:
            boolean: True if the tubes are equal, False otherwise
        """
        return self.balls == other.balls

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

    def clone(self):
        """Clone a tube

        Returns:
            Tube: New cloned tube
        """
        return copy.deepcopy(self)

    def is_completed(self):
        """Check if tube is completed

        Returns:
            boolean: True if tube is completed, False otherwise
        """
        return self.all_same_colored() and self.is_full()


class Game:
    def __init__(self, tubes: list) -> None:
        """Initializes Game

        Args:
            tubes (list): Current tubes in the gamestate
        """
        self.tubes = tubes
        self.num_of_colors = self.calculate_colors()

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

    def expand(self):
        """Expand the current game state

        Returns:
            list: List of possible moves
        """
        moves = []
        for to_index in range(0, len(self.tubes)):
            if self.tubes[to_index].is_full():
                continue
            from_indexes = self.find_moves_from_tube(to_index)
            for from_idx in from_indexes:
                moves.append((from_idx, to_index))
        return moves

    def find_moves_from_tube(self, to_index: int):
        """Get the possible moves from a tube

        Args:
            to_index (int): Index of the tube to move the ball into

        Returns:
            list: List with the indexes of the tubes that can move a ball to the given index
        """
        indexes = []
        to_tube = self.tubes[to_index]
        for from_index in range(0, len(self.tubes)):
            if from_index == to_index:
                continue
            if self.tubes[from_index].is_empty():
                continue
            if to_tube.is_empty() or self.tubes[from_index].get_ball() == to_tube.get_ball():
                indexes.append(from_index)
        return indexes

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

    def get_tubes(self):
        """Getter for tubes

        Returns:
            list: List of Tubes
        """
        return self.tubes

    def __eq__(self, other):
        """Check if two gamestates are equal

        Args:
            other (Game): Gamestate to compare

        Returns:
            boolean: True if both gamestates are the same, False otherwise
        """
        for tube in self.tubes:
            if tube not in other.tubes:
                return False
        return True

    def print(self):
        """Print a game state
        """
        for places in range(3, -1, -1):
            for tube in self.tubes:
                tube.print(places)
            print("")

        print(" --- " * len(self.tubes))

    def clone(self):
        """Clone a gamestate

        Returns:
            Game: New cloned gamestate
        """
        return copy.deepcopy(self)

