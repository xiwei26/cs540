import simulator as sim
import heapq
from itertools import count
import itertools
import copy
import numpy as np
import time
from importlib import reload
reload(sim)

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
    current = None
    while not frontier.empty():
        current = frontier.get()
        if goal(current):
            break
        for successor in successors(current):
            new_cost = cost_so_far[current.drone_position] + np.linalg.norm(np.subtract(current.drone_position,successor.drone_position))
            if successor.drone_position not in cost_so_far or new_cost < cost_so_far[successor.drone_position]:
                cost_so_far[successor.drone_position] = new_cost
                priority = new_cost + heuristic(successor)
                frontier.put(successor, priority)
                came_from[successor.drone_position] = current
    path = [current]
    while not path[-1].drone_position == start.drone_position:
        path.append(came_from[path[-1].drone_position])
    path = list(reversed(path))
    return path

def move_drone_to_position(start,goal):
    goal_test = lambda s: s.drone_position == goal.drone_position
    h = lambda s: heuristic(s,goal)
    successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
    path = a_star_search(start,goal_test,successors,h)
    return path

def valid_actions_planner(state):
    blocks_to_move = []
    valid_destinations = []
    for block_position in state.blocks:
        above = sim.above(block_position)
        if not above in state.blocks:
            valid_destinations.append(above)
            blocks_to_move.append(block_position)
    for x,z in itertools.product(range(sim.MIN_X,sim.MAX_X+1),range(sim.MIN_Z,sim.MAX_Z+1)):
        position = (x,0,z)
        if not position in state.blocks:
            valid_destinations.append(position)
    valid_actions = []
    for block in blocks_to_move:
        for destination in valid_destinations:
            if destination != sim.above(block):
                valid_actions.append((block,destination))
    return valid_actions

def take_action_planner(state,action):
    global planner_states_visited
    planner_states_visited += 1
    state = copy.deepcopy(state)
    state.blocks[action[1]] = state.blocks[action[0]]
    state.drone_position = sim.above(action[1])
    del state.blocks[action[0]]
    return state

def high_level_heuristic(state,goal):
    heuristic = 0
    for position in state.blocks:
        if position in goal.blocks and state.blocks[position] == goal.blocks[position]:
            continue
        for goal_position in goal.blocks:
            if state.blocks[position] == goal.blocks[goal_position]:
                if False:
                    (x1, y1, z1) = position
                    (x2, y2, z2) = goal_position
                    heuristic += abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)
                else:
                    heuristic += np.linalg.norm(np.subtract(position,goal_position))
            if position == goal_position:
                heuristic += 100
            above = sim.above(position)
            while above in state.blocks:
                heuristic += 100
                above = sim.above(above)
    return heuristic
                
def hill_climb_search(start,goal,heuristic):
    print('hill climbing')
    plan = [start]
    actions = []
    last_heuristic = 0
    while not goal(plan[-1]):
        next_actions = valid_actions_planner(plan[-1])
        best_step = None
        best_action = None
        best_heuristic = float('inf')
        for action in next_actions:
            successor = take_action_planner(plan[-1],action)
            current_heuristic = heuristic(successor) + np.linalg.norm(np.subtract(successor.drone_position,action[0]))
            if current_heuristic < best_heuristic:
                best_heuristic = current_heuristic
                best_action = action
                best_step = successor
        plan.append(best_step)
        actions.append(best_action)
        if best_heuristic == last_heuristic:
            breakls
        last_heuristic = best_heuristic
    return plan,actions

def visualize():
    sim.animate(plan, framerate=1, ignore_drone=True)

experiment = 'pyramid'
start = sim.load_state('experiments/' + experiment + '_start.txt')
goal = sim.load_state('experiments/' + experiment + '_goal.txt')
goal_test = lambda s: s == goal
successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
h0 = lambda s: heuristic(s,goal)

planner_goal = lambda s: sim.equal(s,goal)
planner_successors = lambda s: [take_action_planner(s,a) for a in valid_actions_planner(s)]
planner_h = lambda s: high_level_heuristic(s,goal)

sim.states_visited = 0
planner_states_visited = 0
t0 = time.time()
plan, actions = hill_climb_search(start, planner_goal, planner_h)
print('finished plan in',time.time()-t0,'seconds')
print('finding paths')
full_path = [start]
for action in actions:
    goal_state = copy.deepcopy(full_path[-1])
    goal_state.drone_position = sim.above(action[0])
    full_path += move_drone_to_position(full_path[-1],goal_state)[1:]
    full_path.append(sim.take_action(full_path[-1],sim.ACTION_ATTACH))
    goal_state = copy.deepcopy(full_path[-1])
    goal_state.drone_position = sim.above(action[1])
    full_path += move_drone_to_position(full_path[-1],goal_state)[1:]
    full_path.append(sim.take_action(full_path[-1],sim.ACTION_DETACH))
goal_state = copy.deepcopy(full_path[-1])
goal_state.drone_position = (0,5,5)
full_path += move_drone_to_position(full_path[-1],goal_state)[1:]
t1 = time.time()

print('completed in',t1-t0,'seconds')
print('number of states visited:',sim.states_visited + planner_states_visited)
print('length of plan:',len(full_path))
print('saving video')
sim.animate(full_path,framerate=4)
