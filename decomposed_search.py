import simulator as sim
import heapq
from itertools import count
import itertools
import copy

class PriorityQueue:
    def __init__(self):
        self.elements = []
        self._counter = count()
    def empty(self):
        return len(self.elements) == 0
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, next(self._counter), item))
    def get(self):
        return heapq.heappop(self.elements)[2]

def heuristic(state, goal):
    (x1, y1, z1) = state.drone_position
    (x2, y2, z2) = goal.drone_position
    return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))

def a_star_search(start, goal, successors, heuristic):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    came_from[start.drone_position] = None
    cost_so_far = {}
    cost_so_far[start.drone_position] = 0
    while not frontier.empty():
        current = frontier.get()
        if goal(current):
            break
        for successor in successors(current):
            new_cost = cost_so_far[current.drone_position] + 1
            if successor.drone_position not in cost_so_far or new_cost < cost_so_far[successor.drone_position]:
                cost_so_far[successor.drone_position] = new_cost
                priority = new_cost + heuristic(successor)
                frontier.put(successor, priority)
                came_from[successor.drone_position] = current
    return came_from


def move_drone_to_position(start,goal):
    goal_test = lambda s: s == goal_state
    h = lambda s: heuristic(s,goal_state)
    search = a_star_search(start,goal_test,successors,h)
    path = [goal_state]
    while not path[-1].drone_position == start.drone_position:
        path.append(search[path[-1].drone_position])
    path = list(reversed(path))
    return path

def valid_actions_planner(state):
    blocks_to_move = []
    valid_destinations = []
    for block_position in state.blocks:
        above = sim.add_tuple(block_position,(0,0,1))
        if not above in state.blocks:
            valid_destinations.append(above)
            blocks_to_move.append(block_position)
    for x,y in itertools.product(range(sim.MIN_X,sim.MAX_X+1),range(sim.MIN_Y,sim.MAX_Y+1)):
        position = (x,y,0)
        if not position in state.blocks:
            valid_destinations.append(position)
    valid_actions = []
    for block in blocks_to_move:
        for destination in valid_destinations:
            if destination != sim.add_tuple(block,(0,0,1)):
                valid_actions.append((block,destination))
    return valid_actions

def take_action_planner(state,action):
    state = copy.deepcopy(state)
    state.blocks[action[1]] = state.blocks[action[0]]
    del state.blocks[action[0]]
    return state

def high_level_heuristic(state,goal):
    #1st: distance between block destination and current position
    heuristic = 0
    for current_position in state.blocks:
        for goal_position in goal.blocks:
            if state.blocks[current_position] == goal.blocks[goal_position] and current_position == goal_position:
                break
            if state.blocks[current_position] == goal.blocks[goal_position]:
                (x1, y1, z1) = current_position
                (x2, y2, z2) = goal_position
                heuristic += max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))
            if current_position == goal_position:
                heuristic += current_position[2] + 1
            #if there are blocks above this one add to heuristic
            above = sim.add_tuple(current_position,(0,0,1))
            while above in state.blocks:
                heuristic += above[2]
                above = sim.add_tuple(above,(0,0,1))
    return heuristic
                
def hill_climb_search(start,goal,successors,heuristic):
    print('hill climbing')
    plan = [start]
    while not goal(plan[-1]):
        next_steps = successors(plan[-1])
        best_step = next_steps[0]
        best_heuristic = heuristic(best_step)
        for successor in next_steps:
            current_heuristic = heuristic(successor)
            if current_heuristic < best_heuristic:
                best_heuristic = current_heuristic
                best_step = successor
        plan.append(best_step)
        sim.plot(best_step, ignore_drone = True)
    return plan

#start = sim.load_state('start.txt')
#goal_state = sim.load_state('goal.txt')
#goal_state.drone_position = (2,3,4)
start = sim.load_state('reversed_start.txt')
goal_state = sim.load_state('reversed_goal.txt')
goal_test = lambda s: s == goal_state
successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
h0 = lambda s: heuristic(s,goal_state)

#path = move_drone_to_position(start,goal_state)
'''
sim.plot(start)
sim.plot(goal_state)
for a in path:
    sim.plot(a)
'''
planner_goal = lambda s: sim.equal(s,goal_state)
planner_successors = lambda s: [take_action_planner(s,a) for a in valid_actions_planner(s)]
planner_h = lambda s: high_level_heuristic(s,goal_state)
plan = hill_climb_search(start, planner_goal, planner_successors,planner_h)

def visualize():
    for step in plan:
        sim.plot(step, ignore_drone = True)

'''
Overview: Decompose search problem into 2 parts: 1 plans where blocks need to be moved, other figures out how to move them there

Pseudo code:

def figure_out_which_block_to_move_and_where(state,goal):
    #valid moves for the high level agent are any
    #blocks with nothing above them to any other position on top of a block
    #this can accept a heuristic
    #can also consider distance between a block and its destination
    #beyond all this use normal search

def move_drone(start,destination):
    A*search from start to destination

while not goal:
    figure_out_which_block_to_move_and_where
    move_drone above block_to_move
    attach drone
    move_drone above destination


'''
