import simulator as sim
import heapq
from itertools import count
import itertools
import copy
import numpy as np

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
            return came_from, current
        for successor in successors(current):
            #new_cost = cost_so_far[current.drone_position] + 1
            new_cost = cost_so_far[current.drone_position] + np.linalg.norm(np.subtract(current.drone_position,successor.drone_position))
            if successor.drone_position not in cost_so_far or new_cost < cost_so_far[successor.drone_position]:
                cost_so_far[successor.drone_position] = new_cost
                priority = new_cost + heuristic(successor)
                frontier.put(successor, priority)
                came_from[successor.drone_position] = current
    print('error: a* could not find goal')

def move_drone_to_position(start,goal):
    goal_test = lambda s: s.drone_position == goal.drone_position
    h = lambda s: heuristic(s,goal)
    successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
    search,end = a_star_search(start,goal_test,successors,h)
    path = [end]
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
    for position in state.blocks:
        if position in goal.blocks and state.blocks[position] == goal.blocks[position]:
            continue
        for goal_position in goal.blocks:
            if state.blocks[position] == goal.blocks[goal_position]:
                (x1, y1, z1) = position
                (x2, y2, z2) = goal_position
                #heuristic += max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))
                heuristic += abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)
            if position == goal_position:
                heuristic += 100
            #if there are blocks above this one add to heuristic
            above = sim.add_tuple(position,(0,0,1))
            while above in state.blocks:
                heuristic += 100
                above = sim.add_tuple(above,(0,0,1))
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
            current_heuristic = heuristic(successor)
            if current_heuristic < best_heuristic:
                best_heuristic = current_heuristic
                best_action = action
                best_step = successor
        plan.append(best_step)
        actions.append(best_action)
        print(best_heuristic)
        if best_heuristic == last_heuristic:
            break
        last_heuristic = best_heuristic
        #sim.plot(best_step, ignore_drone = True)
    return plan,actions

start = sim.load_state('pyramid_start.txt')
goal_state = sim.load_state('pyramid_goal.txt')
goal_test = lambda s: s == goal_state
successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
h0 = lambda s: heuristic(s,goal_state)

planner_goal = lambda s: sim.equal(s,goal_state)
planner_successors = lambda s: [take_action_planner(s,a) for a in valid_actions_planner(s)]
planner_h = lambda s: high_level_heuristic(s,goal_state)
#plan, actions = hill_climb_search(start, planner_goal, planner_h)

def visualize():
    for step in plan:
        sim.plot(step, ignore_drone = True)

#visualize()

full_path = [start]
for action in actions:
    goal_state = copy.deepcopy(full_path[-1])
    goal_state.drone_position = sim.add_tuple(action[0],(0,0,1))
    full_path += move_drone_to_position(full_path[-1],goal_state)[1:]
    full_path.append(sim.take_action(full_path[-1],sim.ACTION_ATTACH))
    goal_state = copy.deepcopy(full_path[-1])
    goal_state.drone_position = sim.add_tuple(action[1],(0,0,1))
    full_path += move_drone_to_position(full_path[-1],goal_state)[1:]
    full_path.append(sim.take_action(full_path[-1],sim.ACTION_DETACH))
goal_state = copy.deepcopy(full_path[-1])
goal_state.drone_position = (0,5,5)
full_path += move_drone_to_position(full_path[-1],goal_state)[1:]
#for step in full_path:
#    sim.plot(step)
print('saving video')
sim.save_video(full_path,framerate=32)
