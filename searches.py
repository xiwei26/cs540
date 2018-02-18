import random

def bfs(start, goalf, successorsf):
    if goalf(start):
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

def random_restart_search(start, goalf, successorf, heuristicf):
    '''try messing with restart_counter'''
    # also need to add proper heuristic

    #if heuristic is not changing substantially
    
    path = [start]
    restart_counter = 0
    while not goalf(path[-1]):
        restart_counter += 1
        if restart_counter == 6:
            path = [start]
            restart_counter = 0
        path.append(random.choice(successorf(path[-1])))
    return path

def random_backtrack(start, goalf, successorf):
    path = [start]
    restart_counter = 0
    while not goalf(path[-1]):
        restart_counter += 1
        if restart_counter == 6:
            path = path[:random.randint(1,len(path))]
            restart_counter = 0
        path.append(random.choice(successorf(path[-1])))
    return path
