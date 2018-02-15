import testSim
import time

def heuristic(current_state,goal):
    return 0

def save_video(path):
    os.system('rm *.mp4')
    for i,state in enumerate(path):
        testSim.plot(state,str(i) + ".png")
    os.system("ffmpeg -r 2 -i %d.png -v 8 -vf \"zoompan=d=1+'2*eq(in,1)'+'2*eq(in," + str(len(path)) + ")'\" -vcodec mpeg4 -y movie.mp4")
    os.system('rm *.png')

def bfs(start, goalf, successorsf):
    if start == goal:
        return [start]
    path = lambda state: path(explored[state]) + [state] if state in explored else [state]
    explored = {start:None}
    frontier = [start]
    while frontier:
        state = frontier.pop()
        successors = [s for s in successorsf(state) if not s in explored]
        for successor in successors:
            explored[successor] = state
            if goalf(successor):
                return path(successor)[1:]
        frontier = successors + frontier

testSim.states_visited = 0
start = testSim.load_state('start.txt')
goal = testSim.load_state('goal.txt')

t0 = time.time()

goal_test = lambda s: testSim.equal(s,goal)
successors = lambda s: [testSim.take_action(s,a) for a in testSim.valid_actions(s)]

search = bfs(start,goal_test,successors)

t1 = time.time()

print('RUNNING breadth first search')
print('number of states visited:',testSim.states_visited)
print('time to run search:',t1-t0)
print('length of plan:',len(search)-1)
save_video(search)
