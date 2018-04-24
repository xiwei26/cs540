import math
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

def distance(a,b):
    (x1, y1, z1) = a
    (x2, y2, z2) = b
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)
    
def heuristic(state, goal):
    return distance(state.drone_position,goal)

def a_star_search(start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    came_from[start.drone_position] = None
    cost_so_far = {}
    cost_so_far[start.drone_position] = 0
    current = None
    states_visited = 0
    while not frontier.empty():
        current = frontier.get()
        if current.drone_position == goal:
            break
        for action in sim.valid_actions(current):
            successor = sim.take_action(current,action)
            states_visited += 1
            new_cost = cost_so_far[current.drone_position] + distance(current.drone_position,successor.drone_position)
            if successor.drone_position not in cost_so_far or new_cost < cost_so_far[successor.drone_position]:
                cost_so_far[successor.drone_position] = new_cost
                priority = new_cost + heuristic(successor, goal)
                frontier.put(successor, priority)
                came_from[successor.drone_position] = current
    path = [current]
    while not path[-1].drone_position == start.drone_position:
        path.append(came_from[path[-1].drone_position])
    path = list(reversed(path))
    sim.states_visited += states_visited
    print(states_visited)
    return path

def greedy_search(start,goal):
    path = [start]
    while path[-1].drone_position != goal:
        best_step = None
        best_heuristic = float('inf')
        for action in sim.valid_actions(path[-1]):
            successor = sim.take_action(path[-1],action)
            h = heuristic(successor,goal)
            if h < best_heuristic:
                best_heuristic = h
                best_step = successor
        path.append(best_step)
    return path

def move_drone(start,goal):
    path = a_star_search(start,goal)
    #path = greedy_search(start,goal)
    return path
