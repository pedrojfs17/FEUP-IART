import copy
from tube import Tube, Game

class Node:
    parent = None

    def __init__(self, gamestate: Game, cost: int = 0, dist: int = 0):
        """Initializes Node

        Args:
            gamestate (Game): Current Gamestate
            cost (int, optional): Cost estimate to the solution. Defaults to 0.
            dist (int, optional): Distance from the initial state. Defaults to 0.
        """
        self.gamestate = gamestate
        self.dist = dist
        self.cost = cost

    def __eq__(self, o):
        """Check if two nodes are equal

        Args:
            o (Node): Node to compare

        Returns:
            boolean: True if both nodes are equal, False otherwise
        """
        return self.gamestate.__eq__(o.gamestate)

    def __hash__(self):
        """Hash Function

        Returns:
            String: Hash for the current Node
        """
        return ".".join([str(tube) for tube in self.gamestate.get_tubes()])

    def print(self):
        """Print node gamestate
        """
        self.gamestate.print()
        print("-----" * len(self.gamestate.tubes))

    def __lt__(self, o):
        """Compares two nodes

        Args:
            o (Node): Node to compare

        Returns:
            boolean: True if this node's total cost is less than the other one, False otherwise
        """
        return (self.dist + self.cost) < (o.dist + o.cost)

    def set_dist(self, dist):
        """Setter for dist

        Args:
            new_dist (int): Distance from the starting node
        """
        self.dist = dist

    def set_cost(self, cost):
        """Setter for cost

        Args:
            cost (int): Estimate of the cost to get to a solution
        """
        self.cost = cost

    def set_parent(self, node):
        """Setter for parent

        Args:
            node (Node): Parent node
        """
        self.parent = node

    def get_total_cost(self):
        """Getter for the total cost

        Returns:
            int: Returns the distance from the starting node plus the estimative to get to the solution
        """
        return self.cost + self.dist

    def clone(self):
        """Clone a node

        Returns:
            Node: New cloned node
        """
        return copy.deepcopy(self)

    def number_of_wrong_heuristics(self):
        """Number of wrong balls in a node heuristics

        This heuristics counts the number of incorrectly placed balls
        along the tubes assuming that it will be needed at least one move
        per ball to put them in the correct place.

        Returns:
            int: Estimate cost to get to the solution
        """
        cost = 0

        for tube in self.gamestate.tubes:
            balls = tube.balls.copy()

            if len(balls) == 0: continue

            idx = next((i for i, v in enumerate(balls) if v != balls[0]), -1)
            if idx == -1: continue

            balls = balls[idx:]
            cost += len(balls)

        return cost

    def number_of_consecutive_heuristics(self):
        """Number of consecutive heuristics

        This heuristics calculates the maximum number of consecutive
        balls of the same color for each color and estimates the cost
        by calculating how many are needed to have the 4 balls of the
        same color in the same tube.

        For example, if there is a blue ball in tube 1 and another in
        tube 2, and there are 2 blue balls in tube 3, since the maximum
        number of consecutive balls is 2, it will be needed at least
        4-2 moves to put all the balls in the same tue.

        Returns:
            int: Estimate cost to get to the solution
        """
        cost = 0
        dic = dict()

        for tube in self.gamestate.tubes:
            balls = tube.balls
            if (len(balls) == 0): continue

            for i in range(0, len(balls)):
                idx = next((x for x, v in enumerate(balls, start=i) if v != balls[i]), -1)
                if idx == -1:
                    dic.setdefault(balls[0], []).append(len(balls) - i)
                    break
                else:
                    dic.setdefault(balls[0], []).append(idx - i)

        for key in dic:
            cost += 4 - max(dic[key])

        return cost

    def node_score_heuristic(self):
        """Node score heuristics

        This heuristics calculates a score based on the number of
        consecutive balls of the same color and the number of empty
        tubes. 
        Although it is not optimal since this isn't a valid heuristics,
        our tests demonstrated that this heuristics converges really 
        fast to every good solution.

        Returns:
            int: Node score, the higher the better
        """
        score = 0

        for tube in self.gamestate.tubes:
            balls = tube.balls.copy()

            if len(balls) == 0:
                score += 10
            else:
                c1 = balls.pop(0)
                cnt = 1
                while len(balls) != 0:
                    c2 = balls.pop(0)
                    if c1 == c2:
                        cnt += 1
                    else:
                        c1 = c2
                        cnt = 1
                score += (5 * cnt)

        return score


class Graph:

    def __init__(self, depth=None, visited=None):
        """Initializes Graph

        Args:
            depth (List, optional): Visited nodes organized by depth. Defaults to None.
            visited (List, optional): Visited nodes. Defaults to None.
        """
        self.depth = [] if depth is None else depth
        self.visited = [] if visited is None else visited

    def new_depth(self):
        """Add a new depth to the depth list
        """
        self.depth.append([])

    def add_node(self, node: Node, level):
        """Add a node to the depths list

        Args:
            node (Node): Visited node
            level (int): Node's depth
        """
        while len(self.depth) < level:
            self.new_depth()

        self.depth[level - 1].append(node)

    def visit(self, node: Node):
        """Add Node to visited

        Args:
            node (Node): Visited Node
        """
        self.visited.append(node)

    def path(self, dest):
        """Get a path from the starting node to the destination node

        Args:
            dest (Node): Final node

        Returns:
            List: Path from the initial node
        """
        node = dest
        path = [dest]
        while node != self.depth[0][0]:
            path.append(node.parent)
            node = node.parent
        path.reverse()
        return path

    def expanded_states(self):
        """Get number of expanded states

        Returns:
            int: Number of expanded states
        """
        count = 0
        for level in self.depth:
            count += len(level)
        return count
