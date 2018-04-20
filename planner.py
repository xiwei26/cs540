import simulator as sim
import itertools
import copy
import math

states_visited = 0

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
    global states_visited
    states_visited += 1
    state = copy.deepcopy(state)
    state.blocks[action[1]] = state.blocks[action[0]]
    state.drone_position = sim.above(action[1])
    del state.blocks[action[0]]
    return state

max_distance = sim.MAX_X + 1 - sim.MIN_X + sim.MAX_Y + 1 - sim.MIN_Y + sim.MAX_Z + 1 - sim.MIN_Z

#blocks are getting punished for having stuff on top of them even if those blocks aren't needed
def planner_heuristic(state,goal):
    ignored_goals = {}
    heuristic = 0
    for goal_pos in goal.blocks:
        if sim.goal_satisfied(goal_pos,goal,state) and goal_pos not in ignored_goals:
            ignored_goals[goal_pos] = goal.blocks[goal_pos]
    for goal_pos in goal.blocks:
        if goal_pos[1] != '?':
            found_block = False
            for i in range(goal_pos[1]-1,-1,-1):
                for block_pos in state.blocks:
                    if sim.position_equal(block_pos,(goal_pos[0],i,goal_pos[2])):
                        found_block = True
                        break
                if found_block:
                    break
                heuristic += max_distance ** 2
    for position in state.blocks:
        if position in ignored_goals:
            continue
        elif position in goal.blocks:
            heuristic += max_distance ** 4
        min_distance = float('inf')
        for goal_position in goal.blocks:
            if state.blocks[position] == goal.blocks[goal_position]:
                above = sim.above(position)
                while above in state.blocks:
                    heuristic += max_distance ** 4
                    above = sim.above(above)

                x1, y1, z1 = position
                x2, y2, z2 = goal_position
                if x2 == '?':
                    x2 = x1
                if y2 == '?':
                    y2 = y1
                if z2 == '?':
                    z2 = z1
                distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) * max_distance
                droneX,droneY,droneZ = state.drone_position
                destX,destY,destZ = sim.above(position)
                distance += math.sqrt((droneX-destX)**2 + (droneY-destY)**2 + (droneZ-destZ)**2) * max_distance ** .5
                if distance < min_distance:
                    min_distance = distance
        heuristic += min_distance if min_distance != float('inf') else 0
    return heuristic
                
def hill_climb_search(start,goal):
    print('hill climbing')
    plan = [start]
    actions = []
    while not sim.at_goal(plan[-1],goal):
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
    return plan[1:],actions
