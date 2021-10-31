from xlwt import Workbook
from enum import Enum
from graph import Graph, Node, Tube, Game
import json
import time
import random


class Algorithm(Enum):
    """Enum with the algorithms available
    """
    BFS = 1
    DFS = 2
    IDS = 3
    GREEDY = 4
    A_STAR = 5


def expand_node(node: Node, algorithm: Algorithm):
    """Expand node and get the list with all the adjacent nodes

    Args:
        node (Node): Current node
        algorithm (Algorithm): Choosen Algorithm

    Returns:
        list: List with the adjacent nodes
    """
    expansion = []
    moves = node.gamestate.expand()

    for move in moves:
        new_gamestate = node.gamestate.clone()
        from_i, to_i = move
        new_gamestate.move_ball(from_i, to_i)
        new_node = Node(new_gamestate, 0, node.dist + 1)

        if algorithm == Algorithm.GREEDY or algorithm == Algorithm.A_STAR:
            new_node.set_cost(new_node.number_of_wrong_heuristics())

        expansion.append(new_node)

    for children in expansion:
        children.parent = node

    return expansion


def get_stack_item(stack, item):
    """Checks if item is in a list and returns it

    Args:
        stack (list): List with items
        item: Item to be found in list

    Returns:
        Any: Item in the list, if found, None otherwise
    """
    try:
        idx = stack.index(item)
        return stack[idx]
    except:
        return None


def add_states_to_stack(stack, new_states, algorithm: Algorithm, node: Node):
    """Function to add the expanded states to the stack to be expanded later

    This function adds the states according to the algorithm choosen:
        - BFS -> Add the states to the end of the stack
        - DFS/IDS -> Add the states to the front of the stack
        - Greedy -> Add the states to the end of the stack and sort them by the total cost
        - A* -> Check if state is already in the stack. If it isn't already, add it, else
        check if the dist is less than the one already in the stack, and if so, update the node.
        Finish by sorting the nodes by their total cost.

    Args:
        stack (list): Current stack
        new_states (list): States to be added to the stack
        algorithm (Algorithm): Choosen Algorithm
        node (Node): Current node

    Returns:
        list: Stack with the new states
    """
    if algorithm == Algorithm.BFS:
        stack = stack + new_states
    elif algorithm == Algorithm.DFS or algorithm == Algorithm.IDS:
        stack = new_states + stack
    elif algorithm == Algorithm.GREEDY:
        stack = stack + new_states
        stack.sort(key=lambda x: x.cost)
    elif algorithm == Algorithm.A_STAR:
        for children in new_states:
            stack_node = get_stack_item(stack, children)
            if stack_node is not None:
                if children.get_total_cost() < stack_node.get_total_cost():
                    stack_node.set_parent(node)
                    stack_node.set_dist(node.dist + 1)
            else:
                stack.append(children)

        stack.sort(key=lambda x: x.get_total_cost())

    return stack


def check_final_depth_solution(expanded: list):
    """Check if any node in the final search depth is a final state

    Args:
        expanded (list): List of nodes to check

    Returns:
        Node: Solution, if found, None otherwise
    """
    for node in expanded:
        if node.gamestate.finished():
            print("Found goal!")
            return node

    return None


def solver(start_node: Node, algorithm: Algorithm, max_depth: int = 5000):
    """Solver function to find a solution from a start node

    Args:
        start_node (Node): Start node
        algorithm (Algorithm): Choosen algorithm to find the solution
        max_depth (int, optional): Max depth to search. Defaults to 5000.

    Returns:
        tuple: Graph with the solution node, if found
    """
    graph = Graph()
    stack = [start_node]

    graph.new_depth()
    graph.add_node(start_node, 1)

    graph.new_depth()

    while len(stack) != 0:
        node = stack.pop(0)

        visited_node = get_stack_item(graph.visited, node)
        if visited_node is not None and node.dist >= visited_node.dist:
            continue

        graph.visit(node)
        graph.add_node(node, node.dist + 1)

        if algorithm != Algorithm.IDS and node.gamestate.finished():
            print("Found goal!")
            return graph, node

        expanded = expand_node(node, algorithm)

        if node.dist < max_depth - 1:
            stack = add_states_to_stack(stack, expanded, algorithm, node)
        else:
            solution = check_final_depth_solution(expanded)
            if solution is not None:
                return graph, solution

    return graph, None


def ids(start_node: Node, max_depth: int = 5000):
    """Iterative Deepening Depth-First Search solver

    Args:
        start_node (Node): Start node
        max_depth (int, optional): Maximum depth to search. Defaults to 5000.

    Returns:
        tuple: graph and the final solution, if found
    """
    graph = None
    for depth in range(1, max_depth):
        graph, node = solver(start_node, Algorithm.IDS, depth)
        if node is not None:
            return graph, node

    return graph, None


def print_solution(path: list):
    """Prints each gamestate of a solution

    Args:
        path (list): Path from the start node to the solution
    """
    [x.print() for x in path]


def generate_puzzle(colors: int):
    """Puzzle generator

    Args:
        colors (int): Number of different coloured balls in the puzzle

    Returns:
        Game: Generated Game
    """
    balls_list = []
    for i in range(1, colors + 1):
        color = [i] * 4
        balls_list += color
    random.shuffle(balls_list)

    tubes_list = []
    pos = 0
    for i in range(colors):
        tubes_list.append(Tube(balls_list[pos:pos + 4]))
        pos += 4
    tubes_list.append(Tube([]))
    tubes_list.append(Tube([]))

    return Game(tubes_list)


def create_sheet():
    """Creates a sheet to save solver statistics

    Returns:
        tuple: Tuple with the sheets for each algorithm
    """
    wb = Workbook()
    sheet_A = wb.add_sheet('A_star sheet', True)
    sheet_greedy = wb.add_sheet('Greedy sheet', True)
    sheet_ids = wb.add_sheet('IDS sheet', True)
    sheet_dfs = wb.add_sheet('DFS sheet', True)
    sheet_bfs = wb.add_sheet('BFS sheet', True)
    return wb, sheet_A, sheet_greedy, sheet_ids, sheet_dfs, sheet_bfs


def write_to_sheet(sheet, row, col, exec_time, size, graph, path):
    """Writes algorithm information to the sheet

    Args:
        sheet (Worksheet): Sheet to write to
        row (int): Row to write to
        col (int): Column to write to
        exec_time (double): Algorithm execution time
        size (int): Number of different colors in level
        graph (Graph): Final Graph
        path (list): Path from the start node to a solution
    """
    sheet.write(0, 0, "Expanded States")
    sheet.write(0, 1, "Solution Size")
    sheet.write(0, 2, "Time")
    sheet.write(0, 3, "Puzzle Size")
    sheet.write(row, col, graph.expanded_states())
    if path is not None:
        sheet.write(row, col + 1, len(path))
    else:
        sheet.write(row, col + 1, "Failed")
    sheet.write(row, col + 2, exec_time)
    sheet.write(row, col + 3, size)


if __name__ == "__main__":
    """Main function to test algorithms
    """
    wb, sheet_A, sheet_greedy, sheet_ids, sheet_dfs, sheet_bfs = create_sheet()

    with open('levels.json') as f:
        levels = json.load(f)

    for level in levels:
        tubes = levels[level]['tubes']
        new_tubes = []
        for tube in tubes:
            new_tubes.append(Tube(tube))
        levels[level] = new_tubes

    pos = 0
    result = 1
    for level in levels:
        game = Game(levels[level])
        init_state = Node(game)

        try:
            start = time.perf_counter()
            graph, goal = solver(init_state, Algorithm.A_STAR, 30)
            end = (time.perf_counter() - start)
            write_to_sheet(sheet_A, result, pos, end, game.num_of_colors, graph, graph.path(goal))
        except:
            print("No solution found! - A*")

        try:
            start = time.perf_counter()
            graph, goal = solver(init_state, Algorithm.GREEDY, 30)
            end = (time.perf_counter() - start)
            write_to_sheet(sheet_greedy, result, pos, end, game.num_of_colors, graph, graph.path(goal))
        except:
            print("No solution found! - Greedy")

        try:
            start = time.perf_counter()
            graph, goal = ids(init_state, 60)
            end = (time.perf_counter() - start)
            write_to_sheet(sheet_ids, result, pos, end, game.num_of_colors, graph, graph.path(goal))
        except:
            print("No solution found! - IDS")

        try:
            start = time.perf_counter()
            graph, goal = solver(init_state, Algorithm.DFS, 60)
            end = (time.perf_counter() - start)
            write_to_sheet(sheet_dfs, result, pos, end, game.num_of_colors, graph, graph.path(goal))
        except:
            print("No solution found! - DFS")

        try:
            start = time.perf_counter()
            graph, goal = solver(init_state, Algorithm.BFS, 15)
            end = (time.perf_counter() - start)
            write_to_sheet(sheet_bfs, result, pos, end, game.num_of_colors, graph, graph.path(goal))
        except:
            print("No solution found! - BFS")

        result += 1
        wb.save('Results.xls')
