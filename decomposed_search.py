import simulator as sim
import move_drone
import planner
import copy
import time
from importlib import reload
reload(sim)
reload(move_drone)
reload(planner)

def make_plan(start, goal):
    planner.states_visited = 0
    sim.states_visited = 0
    t0 = time.time()
    plan, actions = planner.hill_climb_search(start, goal)
    print('finished plan in',time.time()-t0,'seconds')
    print('finding paths')
    full_path = [start]
    print (actions)
    for action in actions:
        next_drone_position = sim.above(action[0])
        full_path += move_drone.move_drone(full_path[-1],next_drone_position)
        full_path.append(sim.take_action(full_path[-1],sim.ACTION_ATTACH))
        next_drone_position = sim.above(action[1])
        full_path += move_drone.move_drone(full_path[-1],next_drone_position)
        full_path.append(sim.take_action(full_path[-1],sim.ACTION_DETACH))
    t1 = time.time()
    print('completed in',t1-t0,'seconds')
    print('number of states visited:', sim.states_visited + planner.states_visited)
    print('length of plan:',len(full_path))
    return full_path

experiment = 'test3'
start = sim.load_state('experiments/' + experiment + '_start.txt')
goal = sim.load_state('experiments/' + experiment + '_goal.txt')
full_path = make_plan(start,goal)
print('saving video')
sim.animate(full_path,framerate=16)
