import simulator as sim
import heapq
from itertools import count
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
    (x2, y2, z2) = goal
    return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))

def a_star_search(start, goal, successors):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    came_from[start.drone_position] = None
    cost_so_far = {}
    cost_so_far[start.drone_position] = 0
    current = None
    while not frontier.empty():
        current = frontier.get()
        if current.drone_position == goal:
            break
        for successor in successors(current):
            new_cost = cost_so_far[current.drone_position] + np.linalg.norm(np.subtract(current.drone_position,successor.drone_position))
            if successor.drone_position not in cost_so_far or new_cost < cost_so_far[successor.drone_position]:
                cost_so_far[successor.drone_position] = new_cost
                priority = new_cost + heuristic(successor, goal)
                frontier.put(successor, priority)
                came_from[successor.drone_position] = current
    path = [current]
    while not path[-1].drone_position == start.drone_position:
        path.append(came_from[path[-1].drone_position])
    path = list(reversed(path))
    return path

def move_drone(start,goal):
    successors = lambda s: [sim.take_action(s,a) for a in sim.valid_actions(s)]
    path = a_star_search(start,goal,successors)
    return path
