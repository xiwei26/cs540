import simulator as sim
import itertools
import copy
import math

planner_states_visited = 0

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

def planner_heuristic(state,goal):
    heuristic = 0
    for position in state.blocks:
        if position in goal.blocks and state.blocks[position] == goal.blocks[position]:
            continue
        elif position in goal.blocks:
            heuristic += 30
        above = sim.above(position)
        while above in state.blocks:
            heuristic += 30
            above = sim.above(above)
        min_distance = float('inf')
        for goal_position in goal.blocks:
            if state.blocks[position] == goal.blocks[goal_position]: 
                x1, y1, z1 = position
                x2, y2, z2 = goal_position
                distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
                if distance < min_distance:
                    min_distance = distance
        heuristic += min_distance
    return heuristic
                
def hill_climb_search(start,goal):
    print('hill climbing')
    plan = [start]
    actions = []
    while not sim.equal(plan[-1],goal):
        next_actions = valid_actions_planner(plan[-1])
        best_step = None
        best_action = None
        best_heuristic = float('inf')
        for action in next_actions:
            successor = take_action_planner(plan[-1],action)
            current_heuristic = planner_heuristic(successor,goal)# + np.linalg.norm(np.subtract(plan[-1].drone_position,action[0]))
            if current_heuristic < best_heuristic:
                best_heuristic = current_heuristic
                best_action = action
                best_step = successor
        print(best_heuristic)
        plan.append(best_step)
        actions.append(best_action)
    return plan,actions
