import random

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

def random_restart_search(start, goalf, successorf, heuristicf):
    path = [start]
    restart_counter = 0
    while not goalf(path[-1]):
        restart_counter += 1
        if restart_counter == 6:
            path = [start]
            restart_counter = 0
        path.append(random.choice(successorf(path[-1])))
    return path

#backtrack in random restart search: select a random point in the path and discard everything after that, starting from there
