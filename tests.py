import simulator as sim
import heuristics
import search
import time
from importlib import reload
reload(sim)
reload(heuristics)
reload(search)
        
start = sim.load_state('start.txt')
goal = sim.load_state('goal.txt')
goal_test = lambda s: sim.equal(s,goal)
successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
h0 = lambda s: heuristics.heuristic(s,goal)

def test0():
    sim.states_visited = 0
    t0 = time.time()
    print('RUNNING breadth first search')
    plan = search.bfs(start,goal_test,successors)
    t1 = time.time()
    print('number of states visited:',sim.states_visited)
    print('time to run search:',t1-t0)
    print('length of plan:',len(plan)-1)
    sim.save_video(plan)

def test1():
    sim.states_visited = 0
    t0 = time.time()
    print('RUNNING random restart search')
    plan = search.random_restart_search(start,goal_test,successors,h0)
    t1 = time.time()
    print('number of states visited:',sim.states_visited)
    print('time to run search:',t1-t0)
    print('length of plan:',len(plan)-1)
    sim.save_video(plan)


#test1()
