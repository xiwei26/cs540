import simulator as sim
import heuristics
import searches
import time
from importlib import reload
reload(sim)
reload(heuristics)
reload(searches)
        
start = sim.load_state('start.txt')
goal = sim.load_state('goal.txt')
goal_test = lambda s: sim.equal(s,goal)
successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
h0 = lambda s: heuristics.heuristic(s,goal)

def test(name,search,*search_args):
    sim.states_visited = 0
    print('RUNNING:',name)
    t0 = time.time()
    plan = search(*search_args)
    t1 = time.time()
    print('number of states visited:',sim.states_visited)
    print('time to run search:',t1-t0)
    print('length of plan:',len(plan)-1)
    print('saving video')
    sim.save_video(plan)

def test0():
    test('breadth first search',searches.bfs,start,goal_test,successors)

def test1():
    test('random restart search',searches.random_restart_search,start,goal_test,successors,h0)

def test2():
    test('random backtrack search',searches.random_backtrack,start,goal_test,successors)

for i in range(5):
    test2()
