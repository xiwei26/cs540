import time
#!/usr/bin/python

### IMPORTANT NOTE:
###   If creating a stack of cubes/blocks, the creation of the stack MUST start from the
###   zero level of Y in the input file. Otherwise the cube/block will be considered invalid.
import copy
import math
class Node:
    def __init__(self,state,action,f=0,g=0,h=0):
        self.state = state
        self.f = f
        self.g = g
        self.h = h
        self.action=action
    
    def __repr__(self):
        return "Node(" + repr(self.state) + ", f=" + repr(self.f) + \
               ", g=" + repr(self.g) + ", h=" + repr(self.h) + ")"

class Position:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def getPositionVals(self):
        return str(self.x),str(self.y),str(self.z)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getZ(self):
        return self.z

    def __eq__(self,other):
        return (self.x,self.y,self.z)==(other.x,other.y,other.z)
    def __ne__(self, other):
        return not(self==other)
############################################################################################################
class Cube:
    def __init__(self, posx, posy, posz, color):
        self.position = Position(posx, posy, posz)
        self.key = self.position.__hash__()
        self.color = color

    def getKey(self):
        return self.key

    def getPosition(self):
        return self.position

    def changePosition(self, x,y,z):
        newCube = Cube(x,y,z,self.color)
        return newCube

    def cubeColor(self):
        return self.color

    def copyCube(self, color, x,y,z):
        cpCube = Cube(x,y,z,color)
        return cpCube
    def __eq__(self, other):
        return (self.position, self.key, self.color)==(other.position,other.key,other.color)
    def __ne__(self, other):
        return not(self==other)

##############################################################################################
class Drone:
    def __init__(self, posx, posy, posz):
        self.position = Position(int(posx), int(posy), int(posz))
        self.key = self.position.__hash__()
        self.color = "drone"
        self.cube = None
        self.hasCube = False

    def currentPos(self):
        return self.position

    def setPosition(self, x,y,z):
        self.position = Position(int(x), int(y), int(z))
        self.key = self.position.__hash__()

    def getPosition(self):
        return self.position

    def getKey(self):
        return self.key

    def cubeColor(self):
        return self.color

    def hasCubeAttached(self):
        return self.hasCube

    def attachCube(self, cube):
        print("Attached cube (to drone) vals:", cube.getPosition().getPositionVals(),cube.cubeColor())
        self.cube = cube
        self.hasCube = True

    def moveCube(self,x,y,z):
        self.cube = self.cube.changePosition(x,y,z)

    def cubeObject(self):
        return self.cube

    def dropCube(self, yValue):
        newCube = Cube(int(self.position.getX()),int(yValue),int(self.position.getZ()), str(self.cube.cubeColor()))
        self.cube = None
        self.hasCube = False
        return newCube

    def __eq__(self,other):
        return (self.position,self.key)==(other.position,other.key)


     # Need to make sure that the move is through unblocked space
        #def move(self, position):

##############################################################################################
class DroneWorld:
    def __init__(self, fileName):
        self.fileName = fileName
        self.droneExists = False
        self.globe = {}
        self.cubeList = []
        self.floatingCubeList = []
        self.processFile(fileName)
        self.processList(self.cubeList,self.floatingCubeList)
        self.trackValidDroneMoves = 0
        self.trackInvalidDroneMoves = 0
        self.trackValidCubeMoves = 0
        self.trackInvalidCubeMoves = 0
        self.trackInvalidDronePickup = 0
        self.trackValidDronePickup = 0
        self.trackValidDroneRelease = 0
        self.trackInvalidDroneRelease = 0

    def processFile(self,fileName):
        fileIn = open(fileName, 'r')
        self.worldFill = fileIn.readlines()
        fileIn.close()
        self.droneAccountedFor = False

        for line in self.worldFill:
            state = False
            line = line.strip()
            values = line.split(',')
            #print("Values: ", line)
            #print("values---: ", values)

            if self.validateXZVal(values[0]):
                if self.validateValY(values[1]):
                    if self.validateXZVal(values[2]):
                        state = True
                    else:
                        print("INVALID Z Value: ", values[2])
                        continue
                else:
                    print("INVALID Y Value: ", values[1])
                    continue
            else:
                print("INVALID X Value: ", values[0])
                continue

            #print("Values:" + str(values[0]) + ", " + str(values[1]) + ", " + str(values[2]))
            # ignore invalid entries
            if state:
                if ('drone' == values[3]) and (self.droneExists is True):
                    print("Only 1 drone allowed per simulation, dropping one")
                    continue
                elif('drone' == values[3]) and (self.droneExists is False):
                    self.drone = Drone(int(values[0]),int(values[1]),int(values[2]))
                    self.cubeList.append(self.drone)
                    self.droneAccountedFor = True
                    self.droneExists = True
                else:
                    cubeRtn = Cube(int(values[0]),int(values[1]),int(values[2]),values[3])
                    if int(values[1]) > 0:
                        self.floatingCubeList.append(cubeRtn)
                    else:
                        self.cubeList.append(cubeRtn)
        if not self.droneAccountedFor:
            print("#####################################################")
            print("WARNING, no Drone has been passed into the simulation\n")
            print("#####################################################")

    def processList(self, inList, floatList):
        for entry in inList:
            self.globe[entry.getKey()] = entry # Add the position to the globe

        for floater in floatList:
            tstX = floater.getPosition().getX()
            tstY = floater.getPosition().getY()
            tstZ = floater.getPosition().getZ()
            tmpKey = hashPosition(int(tstX),(int(tstY)-1),int(tstZ))
            if self.globe.get(tmpKey) is None:
                print("Found:", self.globe.get(floater.getKey()))
                print("ERROR: Cube is floating in space, invalid cube Y position",floater.getPosition().getPositionVals(), floater.cubeColor())
                continue
            else:
                self.globe[floater.getKey()] = floater # Add the position to the globe

    def state(self):
        return self.globe
    def printState(self):
        currState = self.state()
        for key in currState:
            print("vals:", currState[key].position.getPositionVals(), ", color:", currState[key].cubeColor())

    def move(self,x,y,z):
        self.Validatemove(x,y,z)
        ## finally move the drone
        #print("old drone pos:", self.drone.position.getPositionVals())
        self.globe.pop(self.drone.getKey(), None)
        xVal= self.drone.position.getX()+x

        yVal= self.drone.position.getY()+y
        zVal= self.drone.position.getZ()+z
        yValCube = yVal - 1
        self.drone.setPosition(xVal,yVal,zVal)
        self.globe[self.drone.getKey()] = self.drone
        #print("....new drone pos (from drone):", self.drone.position.getPositionVals())
        #print("....new drone pos confirmed (from globe):", self.globe.get(hashPosition(xVal,yVal,zVal)))

        if self.drone.hasCubeAttached() is True:
            #print("--Drone has cube, moving cube to:",xVal,yValCube,zVal)
            oldCube = self.drone.cubeObject()
            oldCubeKey = oldCube.getKey()
            #print("===old cube data, coords: ",oldCube.getPosition().getX(),oldCube.getPosition().getY(),oldCube.getPosition().getZ())
            #print("===old cube data, key", oldCube.getKey(), oldCubeKey)
            #print("===old cube data, color", oldCube.cubeColor())

            self.drone.moveCube(xVal,yValCube,zVal)#creates a new cube in drone
            self.globe.pop(oldCubeKey, None)#get rid of the old cube
            #print("===NEW cube data, key:", self.drone.cubeObject().getKey())
            newCubeKey = self.drone.cubeObject().getKey()
            newCubeColor = str(self.drone.cubeObject().cubeColor())
            newCubeColor = newCubeColor.strip('{}')
            #print("===NEW cube data, color:", str(self.drone.cubeObject().cubeColor()))

            self.globe[newCubeKey] = self.drone.cubeObject()
            
            #print("....new cube pos (from drone):", self.drone.cubeObject().getPosition().getPositionVals())
            #print("....new cube pos confirmed (from globe)xyz:", self.globe.get(hashPosition(xVal,yValCube,zVal)))
            #print("....new cube pos confirmed (from globe)cubekey:", self.globe.get(self.drone.cubeObject().getKey()))
            self.trackValidCubeMoves += 1

        else: #remove prior jve
            #print("No cube")##remove prior jve
            pass

        return True

    def Attach(self):
        dronePos = self.drone.getPosition()
        # attach the cube to the drone
        if self.ValidAttach() is False:
            return False
        checkForCube = self.globe.get(
            hashPosition(int(dronePos.getX()), (int(dronePos.getY()) - 1), int(dronePos.getZ())))
        attCube = Cube(int(dronePos.getX()), (int(dronePos.getY()) - 1), int(dronePos.getZ()), checkForCube.cubeColor())
        # print("attCube vals:", attCube.getKey(),attCube.cubeColor())
        self.drone.attachCube(attCube)
        self.trackValidDronePickup += 1
    def ValidAttach(self):
        #print("Drone attach")
        dronePos = self.drone.getPosition()

        # will have a cube if valid
        checkForCube = self.globe.get(hashPosition(int(dronePos.getX()), (int(dronePos.getY())-1), int(dronePos.getZ())))
        if checkForCube is None:
            #print("ERROR: Invalid Drone pickup, no cube below Drone position:",dronePos.getX(),dronePos.getY(),dronePos.getZ())
            self.trackInvalidDronePickup += 1
            return False
        if self.drone.hasCubeAttached()==True:
            return False
       #print("Color of P/U cube: ", checkForCube.cubeColor())
        return True

    def Release(self):
        #print("Drone release")
        if self.drone.hasCubeAttached() is False:
            self.trackInvalidDroneRelease += 1
            print("ERROR: Drone is not carrying a cube")
            return False
        #determine current Y position of drone/cube
        currY = self.drone.getPosition().getY()
        #print("Current drone Y value:", currY)
        currY -= 1 #the cube i case it's at 0

        if currY > 0:
            #print("Y is above 0:",currY)
            #find out how far down, Y direction, it can go
            drnZ = int(self.drone.getPosition().getZ())
            drnX = int(self.drone.getPosition().getX())
            tmpKey = hashPosition(drnX,(currY-1), drnZ)
            #print("Current drone position values:",drnX,currY, drnZ)

            while (self.globe.get(tmpKey) is None) and (currY > -1):
                #print("The space occupied?:",self.globe.get(tmpKey,None) )
                currY -= 1 ## next spot down
                tmpKey = hashPosition(drnX,currY,drnZ)
                #print("Dropping down, determining Y for release:",currY)
            if self.globe.get(tmpKey) is not None:
                currY += 1

        #print("Drone release Valid at 0 level")
        oldCube = self.drone.cubeObject()
        oldCubeKey = oldCube.getKey()
        self.globe.pop(oldCubeKey, None)
        dpCube = self.drone.dropCube(currY)
        self.globe[dpCube.getKey()] = dpCube #str(dpCube.cubeColor())
        self.trackValidDroneRelease += 1


    def Speak(self):
        print("Drone position is:", self.drone.position)

    def reportValidDroneMoves(self):
        return self.trackValidDroneMoves

    def reportInvalidDroneMoves(self):
        return self.trackInvalidDroneMoves

    def reportValidCubeMoves(self):
        return self.trackValidCubeMoves

    def reportInvalidCubeMoves(self):
        return self.trackInvalidCubeMoves

    def reportInvalidDronePickup(self):
        return self.trackInvalidDronePickup

    def reportValidDronePickup(self):
        return self.trackValidDronePickup

    def reportValidDroneRelease(self):
        return self.trackValidDroneRelease

    def reportInvalidDroneRelease(self):
        return self.trackInvalidDroneRelease

    def validateXZVal(self, val):
        if int(val) < -50:
            return False
        elif int(val) > 50:
            return False
        return True

    def validateValY(self, Yval):
        if int(Yval) < 0:
            return False
        if int(Yval) > 50:
            return False
        return True

    def validateDroneMove(self, dVal):
        if int(dVal < -1):
            return False
        elif int(dVal > 1):
            return False
        return True
    def Validatemove(self,x,y,z):
        if self.droneExists is False:
            print("##############################################################")
            print("ERROR NO Drone is in the simulation, movement will not be made")
            print("##############################################################")
            self.trackInvalidDroneMoves += 1
            #print("1")
            return False

        if self.validateDroneMove(x):
            if self.validateDroneMove(y):
                if self.validateDroneMove(z):
                    #print("--Valid Drone move")
                    pass
                else:
                    print("--INVALID Drone move Z Value: ", z)
                    self.trackInvalidDroneMoves += 1
                    #print("2")
                    return False
            else:
                print("--INVALID Drone move Y Value: ", y)
                self.trackInvalidDroneMoves += 1
                #print("3")
                return False
        else:
            print("--INVALID Drone move X Value: ", x)
            self.trackInvalidDroneMoves += 1
            #print("4")
            return False

        # Remember also have to move a cube if attached <<<<<<<<<<<<<<<
        ## Create the delta values
        xVal = self.drone.position.getX()

        xVal += int(x)
        if self.validateXZVal(xVal) is False:
            print("--INVALID Drone move, ERROR: X value is beyond the edge of the globe.")
            self.trackInvalidDroneMoves += 1
            # print("5")
            return False
        yVal = self.drone.position.getY()
        yVal += int(y)

        if self.validateValY(yVal) is False:
            #   print("ERROR: Invalid Y move value for Drone results in Y =", yVal)
            self.trackInvalidDroneMoves += 1
            #print("6")
            return False
        zVal = self.drone.position.getZ()
        zVal += int(z)

        if self.validateXZVal(zVal) is False:
            print("--INVALID Drone move, ERROR: X value is beyond the edge of the globe.")
            self.trackInvalidDroneMoves += 1
            #print("7")
            return False
        yValCube = yVal - 1
        #print("position2 xvals:",xVal,yVal,zVal)

        ## check that the position is open if drone has a cube
        ## problem going just vertical
        if self.drone.hasCubeAttached():
            if int(x) == 0 and int(z)== 0: ##vertical move
                if self.validateValY(yVal) is False:
                    print("\nERROR: Bad Y value, Drone will not move.")
                    self.trackInvalidCubeMoves += 1
                    #print("8")
                    return False
            elif (self.validateValY(yValCube) is False) or (self.globe.get(hashPosition(xVal,yValCube,zVal)) is not None):
                #print("\nERROR: Bad Y value or occupied space for cube, Drone will not move. Occupied space: ",xVal,yValCube,zVal)
                self.trackInvalidCubeMoves += 1
                #print("9")
                return False

        ## check that position is open for drone
        if self.globe.get(hashPosition(xVal,yVal,zVal)) is not None:
            #print("\nERROR: occupied space, Drone will not move. Occupied space: ",xVal,yVal,zVal)
            self.trackInvalidDroneMoves += 1
            #print("10")
            return False

       #print("++Valid Drone move to: ",xVal,yVal,zVal)#logging for reporting
        self.trackValidDroneMoves += 1
        return True


#############################################################
def hashPosition(x,y,z):
    checkPos = Position(x,y,z)
    return checkPos.__hash__()

#def isOccupied(x,y,z):
#    square = Position(x,y,z)

def aStarSearch(startState, actionsF, takeActionF, goalTestF, hF):
    h = hF(startState)
    startNode = Node(state=startState,action=[],f=0+h, g=0, h=h)
    return aStarSearchHelper(startNode, actionsF, takeActionF, goalTestF, hF, float('inf'))

count = 0
def aStarSearchHelper(parentNode, actionsF, takeActionF, goalTestF, hF, fmax):
    global count
    if goalTestF(parentNode.state):
        return ([parentNode.state], parentNode.g)
    ## Construct list of children nodes with f, g, and h values
    actions = actionsF(parentNode.state)
    if not actions:
        return ("failure", float('inf'))
    children = []
    actionsTaken = []
    for action in actions:
        (childState,stepCost) = takeActionF(parentNode.state, action)
        #count=count+1
        #childState.printState()
        #print("action taken: ", count)
        h = hF(childState)
        g = parentNode.g + stepCost
        f = max(h+g, parentNode.f)
        childNode = Node(state=childState,action=action, f=f, g=g, h=h)
        children.append(childNode)
    while True:
        # find best child
        children.sort(key = lambda n: n.f) # sort by f value
        #print(len(children))
        bestChild = children[0]
        #print(bestChild.action)
        #bestChild.state.printState()

        if bestChild.f > fmax:
            return ("failure",bestChild.f)
        # next lowest f value
        actionsTaken.append(bestChild.action)
        alternativef = children[1].f if len(children) > 1 else float('inf')
        # expand best child, reassign its f value to be returned value
        result,bestChild.f= aStarSearchHelper(bestChild, actionsF, takeActionF, goalTestF,
                                            hF, min(fmax,alternativef))
        if result is not "failure":               
            result.insert(0,parentNode.state)    
            return (result, bestChild.f)

def goalTestF(state, goal):
    return state==goal

def h0(start, end):
    state=start.state()
    goal=end.state()
    totalDistance=0
    dronetocube=99999
    drone=start.drone
    for key in state:
        for key1 in goal:
            if (state[key].cubeColor()==goal[key1].cubeColor()) and (state[key].cubeColor()!="drone"):
                valX=state[key].getPosition().getX()-goal[key1].getPosition().getX()
                valY=state[key].getPosition().getY()-goal[key1].getPosition().getY()
                valZ=state[key].getPosition().getZ()-goal[key1].getPosition().getZ()
                totalDistance+=math.sqrt(valX*valX+valY*valY+valZ*valZ)
    return totalDistance+dronetocube



def h1(start, end):
    state=start.state()
    goal=end.state()
    totalDistance=0
    dronetocube=99999
    drone=start.drone
    for key in state:
        if state[key].cubeColor()!="drone":
            dX=drone.getPosition().getX()-state[key].getPosition().getX()
            dY=drone.getPosition().getX()-state[key].getPosition().getX()
            dZ=drone.getPosition().getX()-state[key].getPosition().getX()
            ddd=math.sqrt(dX*dX+dY*dY+dZ*dZ)
            if ddd< dronetocube:
                dronetocube=ddd
        for key1 in goal:
            if (state[key].cubeColor()==goal[key1].cubeColor()) and (state[key].cubeColor()!="drone"):
                valX=state[key].getPosition().getX()-goal[key1].getPosition().getX()
                valY=state[key].getPosition().getY()-goal[key1].getPosition().getY()
                valZ=state[key].getPosition().getZ()-goal[key1].getPosition().getZ()
                totalDistance+=math.sqrt(valX*valX+valY*valY+valZ*valZ)
    return totalDistance+dronetocube

def h2(start, end):
    state=start.state()
    goal=end.state()
    totalDistance=0
    dronetocube=99999
    drone=start.drone
    for key in state:
        for key1 in goal:
            if (state[key].cubeColor()==goal[key1].cubeColor()) and (state[key].cubeColor()!="drone"):
                valX=state[key].getPosition().getX()-goal[key1].getPosition().getX()
                valY=state[key].getPosition().getY()-goal[key1].getPosition().getY()
                valZ=state[key].getPosition().getZ()-goal[key1].getPosition().getZ()
                totalDistance+=math.sqrt(valX*valX+valY*valY+valZ*valZ)
            elif (state[key].cubeColor()==goal[key1].cubeColor()) and (state[key].cubeColor()!="drone") and (state[key].getPosition()!=goal[key1.getPosition()]):
                dX=drone.getPosition().getX()-state[key].getPosition().getX()
                dY=drone.getPosition().getX()-state[key].getPosition().getX()
                dZ=drone.getPosition().getX()-state[key].getPosition().getX()
                ddd=math.sqrt(dX*dX+dY*dY+dZ*dZ)
                if ddd< dronetocube:
                    dronetocube=ddd
    return totalDistance+dronetocube


def actionsF(droneWorld):
    currState= droneWorld.state()
    drone= droneWorld.drone
    actions=list()
    if droneWorld.Validatemove(0,0,1)==True:
        actions.append(((0,0,1),1))
    if droneWorld.Validatemove(1,0,0)==True:
        actions.append(((1,0,0),1))
    if droneWorld.Validatemove(-1,0,1)==True:
        actions.append(((-1,0,1),1))
    if droneWorld.Validatemove(-1,0,-1)==True:
        actions.append(((-1,0,-1),1))
    if droneWorld.Validatemove(0,0,-1)==True:
        actions.append(((0,0,-1),1))
    if droneWorld.Validatemove(-1,0,0)==True:
        actions.append(((-1,0,0),1))
    if droneWorld.Validatemove(1,0,1)==True:
        actions.append(((1,0,1),1))
    if droneWorld.Validatemove(1,0,-1)==True:
        actions.append(((1,0,-1),1))
    if droneWorld.Validatemove(0,-1,1)==True:
        actions.append(((0,-1,1),1))
    if droneWorld.Validatemove(1,-1,0)==True:
        actions.append(((1,-1,0),1))
    if droneWorld.Validatemove(-1,-1,1)==True:
        actions.append(((-1,-1,1),1))
    if droneWorld.Validatemove(-1,-1,-1)==True:
        actions.append(((-1,-1,-1),1))
    if droneWorld.Validatemove(0,-1,-1)==True:
        actions.append(((0,-1,-1),1))
    if droneWorld.Validatemove(-1,-1,0)==True:
        actions.append(((-1,-1,0),1))
    if droneWorld.Validatemove(1,-1,1)==True:
        actions.append(((1,-1,1),1))
    if droneWorld.Validatemove(1,-1,-1)==True:
        actions.append(((1,-1,-1),1))
    if droneWorld.Validatemove(0,1,1)==True:
        actions.append(((0,1,1),1))
    if droneWorld.Validatemove(1,1,0)==True:
        actions.append(((1,1,0),1))
    if droneWorld.Validatemove(-1,1,1)==True:
        actions.append(((-1,1,1),1))
    if droneWorld.Validatemove(-1,1,-1)==True:
        actions.append(((-1,1,-1),1))
    if droneWorld.Validatemove(0,1,-1)==True:
        actions.append(((0,1,-1),1))
    if droneWorld.Validatemove(-1,1,0)==True:
        actions.append(((-1,1,0),1))   
    if droneWorld.Validatemove(1,1,1)==True:
        actions.append(((1,1,1),1))   
    if droneWorld.Validatemove(1,1,-1)==True:
        actions.append(((1,1,-1),1))
    if droneWorld.Validatemove(0,1,0)==True:
        actions.append(((0,1,0),1))
    if droneWorld.Validatemove(0,-1,0)==True:
        actions.append(((0,-1,0),1))
    if droneWorld.ValidAttach()==True:
        #print("YESSSSSSSSSSSS")
        actions.append(("attach",0))
    if droneWorld.drone.hasCubeAttached()==True:
        actions.append(("release",1))
    return actions

def takeAction(droneWorld, action):
    droneWorld1=copy.deepcopy(droneWorld)
    if action==((0,0,1),1):
        droneWorld1.move(0,0,1)
    if action==((1,0,0),1):
        droneWorld1.move(1,0,0)
    if action==((-1,0,1),1):
        droneWorld1.move(-1,0,1)
    if action==((-1,0,-1),1):
        droneWorld1.move(-1,0,-1)
    if action==((0,0,-1),1):
        droneWorld1.move(0,0,-1)
    if action==((-1,0,0),1):
        droneWorld1.move(-1,0,0)
    if action==((1,0,1),1):
        droneWorld1.move(1,0,1)
    if action==((1,0,-1),1):
        droneWorld1.move(1,0,-1)
    if action==((0,-1,1),1):
        droneWorld1.move(0,-1,1)
    if action==((1,-1,0),1):
        droneWorld1.move(1,-1,0)
    if action==((-1,-1,1),1):
        droneWorld1.move(-1,-1,1)
    if action==((-1,-1,-1),1):
        droneWorld1.move(-1,-1,-1)
    if action==((0,-1,-1),1):
        droneWorld1.move(0,-1,-1)
    if action==((-1,-1,0),1):
        droneWorld1.move(-1,-1,0)
    if action==((1,-1,1),1):
        droneWorld1.move(1,-1,1)
    if action==((1,-1,-1),1):
        droneWorld1.move(1,-1,-1)
    if action==((0,1,1),1):
        droneWorld1.move(0,1,1)
    if action==((1,1,0),1):
        droneWorld1.move(1,1,0)
    if action==((-1,1,1),1):
        droneWorld1.move(-1,1,1)
    if action==((-1,1,-1),1):
        droneWorld1.move(-1,1,-1)
    if action==((0,1,-1),1):
        droneWorld1.move(0,1,-1)
    if action==((-1,1,0),1):
        droneWorld1.move(-1,1,0)
    if action==((1,1,1),1):
        droneWorld1.move(1,1,1)
    if action==((1,1,-1),1):
        droneWorld1.move(1,1,-1)
    if action==((0,1,0),1):
        droneWorld1.move(0,1,0)
    if action==((1,1,-1),1):
        droneWorld1.move(0,-1,0)
    if action==(("attach",0)):
        droneWorld1.Attach()
    if action==(("release",1)):
        droneWorld1.Release()
    return (droneWorld1,1)

################## MAIN ##################### None



if __name__ == "__main__":
    start_time = time.time()
    ourWorld1 = DroneWorld("world1.txt")
    ourWorld2 = DroneWorld("world2.txt")
    totalDistance=0
    result,depth = aStarSearch(ourWorld1, actionsF, takeAction,
                                lambda s: goalTestF(s.state(), ourWorld2.state()),
                               lambda s: h0(s,ourWorld2))
    elapsed_time = time.time() - start_time
    print("path is :")
    for a in result:
        print(a.printState())
    print("Total time: ",elapsed_time)
    

