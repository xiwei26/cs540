import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors
import numpy as np
import itertools
import random
import copy
import csv

ACTION_ATTACH = 0
ACTION_DETACH = 1

size = 50
MIN_X = -size; MAX_X = size
MIN_Y = 0; MAX_Y = size
MIN_Z = -size; MAX_Z = size

COLOR_MAP = {'red':(1,0,0), 'green':(0,1,0), 'blue':(0,0,1), 'white':(.9,.9,.9), 'black':(.1,.1,.1)}

states_visited = 0

def add_tuple(a,b):
    return tuple(sum(x) for x in zip(a,b))

def beneath(position):
    return (position[0],position[1]-1,position[2])

def above(position):
    return (position[0],position[1]+1,position[2])

def is_inbounds(p):
    return p[0] >= MIN_X and p[0] <= MAX_X and p[1] >= MIN_Y and p[1] <= MAX_Y and p[2] >= MIN_Z and p[2] <= MAX_Z

class State:
    def __init__(self):
        self.drone_position = (0,0,0)
        self.drone_attached = False
        self.blocks = {}
    def __eq__(self,other):
        return self.blocks == other.blocks and self.drone_position == other.drone_position and self.drone_attached == other.drone_attached
    def __ne__(self,other):
        return not self.__eq__(other)

def load_state(file_name):
    state = State()
    with open(file_name,'r') as csvfile:
        csvReader = csv.reader(csvfile)
        for row in csvReader:
            read_position = lambda p: row[p] if row[p] == '?' else int(row[p])
            x = read_position(0)
            y = read_position(2)
            z = read_position(1)
            position = (x,y,z)
            if row[3] == 'drone':
                state.drone_position = position
            elif row[3] == '?':
                state.blocks[position] = '?'
            elif row[3] in COLOR_MAP:
                state.blocks[position] = COLOR_MAP[row[3]]
            else:
                state.blocks[position] = (float(row[3]),float(row[4]),float(row[5]))
    return state

def states_equal(a,b):
    return a.blocks == b.blocks

def equal(a,b):
    return a == b or a == '?' or b == '?'

def position_equal(a,b):
    return equal(a[0],b[0]) and equal(a[1],b[1]) and equal(a[2],b[2])

def goal_satisfied(goal_pos,goal,state):
    eq = lambda a,b: a == b or b == '?'
    fills_requirement = lambda b,r: eq(b[0],r[0]) and eq(b[1],r[1]) and eq(b[2],r[2]) and eq(state.blocks[b],goal.blocks[r])
    for block_pos in state.blocks:
        if fills_requirement(block_pos,goal_pos):
            return True
    return False

def at_goal(state,goal):
    eq = lambda a,b: a == b or b == '?'
    fills_requirement = lambda b,r: eq(b[0],r[0]) and eq(b[1],r[1]) and eq(b[2],r[2]) and eq(state.blocks[b],goal.blocks[r])
    requirements = {}
    for goal_position in goal.blocks:
        requirements[(goal_position,goal.blocks[goal_position])] = []
        for block_position in state.blocks:
            if fills_requirement(block_position, goal_position):
                requirements[(goal_position,goal.blocks[goal_position])].append(block_position)
    while requirements:
        min_requirement = min(requirements, key=lambda x: len(requirements[x]))
        if len(requirements[min_requirement]) == 0:
            return False
        block = requirements[min_requirement]
        del requirements[min_requirement]
        for requirement in requirements:
            if block in requirements[requirement]:
                requirements[requirement].remove(block)
    return True
        
def valid_actions(state):
    actions = []
    moves = tuple(itertools.product((-1,0,1), (-1,0,1), (-1,0,1)))
    for move in moves:
        if move == (0,0,0):
            continue
        drone_destination = add_tuple(state.drone_position,move)
        if not drone_destination in state.blocks and is_inbounds(drone_destination):
            if not state.drone_attached:
                actions.append(move)
            attached_destination = beneath(drone_destination)
            if state.drone_attached and not attached_destination in state.blocks and is_inbounds(attached_destination):
                actions.append(move)
    if state.drone_attached:
        actions.append(ACTION_DETACH)
    elif not state.drone_attached and beneath(state.drone_position) in state.blocks:
        actions.append(ACTION_ATTACH)
    return actions
    
def take_action(state,action):
    global states_visited
    states_visited += 1
    state = copy.deepcopy(state)
    if action == ACTION_ATTACH:
        state.drone_attached = True
    elif action == ACTION_DETACH:
        state.drone_attached = False
        detached_block_position = beneath(state.drone_position)
        detached_block = state.blocks[detached_block_position]
        del state.blocks[detached_block_position]
        while not beneath(detached_block_position) in state.blocks and not detached_block_position[1] == 0:
            detached_block_position = beneath(detached_block_position)
        state.blocks[detached_block_position] = detached_block
    elif type(action) == tuple:
        drone_destination = add_tuple(state.drone_position,action)
        if state.drone_attached:
            state.blocks[beneath(drone_destination)] = state.blocks[beneath(state.drone_position)]
            del state.blocks[beneath(state.drone_position)]
        state.drone_position = drone_destination
    elif type(action) == str:
        print(action)
    return state

def to_image(state, ignore_drone=False):
    top_data = np.full((MAX_Z-MIN_Z+1,MAX_X-MIN_X+1,3),.4,dtype=float)
    front_data = np.full((MAX_Y-MIN_Y+2,MAX_X-MIN_X+1,3),1,dtype=float)
    side_data = np.full((MAX_Y-MIN_Y+2,MAX_Z-MIN_Z+1,3),1,dtype=float)
    front_data[0] = .4
    side_data[0] = .4
    for x,y,z in itertools.product(range(MIN_X,MAX_X+1),range(MIN_Y,MAX_Y+1),range(MIN_Z,MAX_Z+1)):
        position = (x,y,z)
        if state.drone_position == position and not ignore_drone:
            drone_color = (0,0,0)
            if state.drone_attached:
                drone_color = (.2,.2,.2)
            top_data[z-MIN_Z,x-MIN_X] = drone_color
            front_data[y-MIN_Y+1,x-MIN_X] = drone_color
            side_data[y-MIN_Y+1,z-MIN_Z] = drone_color
        elif position in state.blocks:
            top_data[z-MIN_Z,x-MIN_X] = state.blocks[position]
            side_data[y-MIN_Y+1,z-MIN_Z] = state.blocks[position]
            front_data[y-MIN_Y+1,x-MIN_X] = state.blocks[position]
    front_data = np.flip(front_data,0)
    side_data = np.flip(side_data,0)
    return front_data,side_data,top_data
    
def create_figure():
    fig,axes = plt.subplots(2,2)
    axes[0,0].set_axis_off()
    axes[0,0].set_title('Front')
    axes[0,1].set_axis_off()
    axes[0,1].set_title('Side')
    axes[1,0].set_axis_off()
    axes[1,0].set_title('Top')
    axes[1,1].set_axis_off()
    return fig,axes

def plot(state,save_to_file = None, ignore_drone=False):
    front,side,top = to_image(state)
    fig,axes = create_figure()
    axes[0,0].imshow(front)
    axes[0,1].imshow(side)
    axes[1,0].imshow(top)
    if save_to_file:
        plt.savefig(save_to_file)
        plt.close()
    else:
        plt.show()

def animate(plan,framerate=2,ignore_drone=False,save=None):
    fig,axes = create_figure()
    front,side,top = to_image(plan[0],ignore_drone)
    im1 = axes[0,0].imshow(front, animated=True)
    im2 = axes[0,1].imshow(side, animated=True)
    im3 = axes[1,0].imshow(top, animated=True)
    def updatefig(frame):
        front,side,top = to_image(frame,ignore_drone)
        im1.set_array(front)
        im2.set_array(side)
        im3.set_array(top)
        return im1,im2,im3,
    ani = animation.FuncAnimation(fig, updatefig, frames=plan, interval=1000/framerate, blit=False)
    if save:
        ani.save(save,dpi=200)
        plt.close()
    else:
        plt.show()
