#!/usr/bin/python

import collections
import queue as qu
import time

### IMPORTANT NOTE:
###   If creating a stack of cubes/blocks, the creation of the stack MUST start from the
###   zero level of Y in the input file. Otherwise the cube/block will be considered invalid.
class Node:
    def __init__(self,state,f=0,g=0,h=0):
        self.state = state
        self.f = f
        self.g = g
        self.h = h

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
        if self.hasCube is True:
            return False
        print("++Attached cube (to drone), cube vals:", cube.getPosition().getPositionVals(),cube.cubeColor())
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

            if values[0] == '?':
                values[0] = 55
                state = True
                if values[2] == '?':
                    values[2] = 55
            else:
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
                    cubeRtn = Cube(int(values[0]),int(values[1]),int(values[2]),str(values[3]))
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
        ##Looking for a cube that's floating, checking for something below it to verify
        for floater in floatList:
            tstX = floater.getPosition().getX()
            tstY = floater.getPosition().getY()
            tstZ = floater.getPosition().getZ()
            ## looking for special condition of ('?',3,'?',red)
            if tstX == 55 or tstZ == 55:
                print("****special case found****")
                self.globe[floater.getKey()] = floater # Add the position to the globe
                continue

            tmpKey = hashPosition(int(tstX),(int(tstY)-1),int(tstZ))
            if self.globe.get(tmpKey) is None:
                print("Found:", self.globe.get(floater.getKey()))
                print("ERROR: Cube is floating in space, invalid cube Y position",floater.getPosition().getPositionVals(), floater.cubeColor())
                continue
            else:
                self.globe[floater.getKey()] = floater # Add the position to the globe

    def state(self):
        return self.globe

    def move(self,x,y,z):
        if self.droneExists is False:
            print("##############################################################")
            print("ERROR NO Drone is in the simulation, movement will not be made")
            print("##############################################################")
            self.trackInvalidDroneMoves += 1
            return False

        if self.validateDroneMove(x):
            if self.validateDroneMove(y):
                if self.validateDroneMove(z):
                    print("++VDM") ##print("++Valid Drone move values")

                else:
                    print("--INVALID Drone move Z Value: ", z)
                    self.trackInvalidDroneMoves += 1
                    return False
            else:
                print("--INVALID Drone move Y Value: ", y)
                self.trackInvalidDroneMoves += 1
                return False
        else:
            print("--INVALID Drone move X Value: ", x)
            self.trackInvalidDroneMoves += 1
            return False

        # Remember also have to move a cube if attached <<<<<<<<<<<<<<<
        ## Create the delta values
        xVal = self.drone.position.getX()
        xVal += int(x)
        if self.validateXZVal(xVal) is False:
            print("--INVALID Drone move, ERROR: X value is beyond the edge of the globe.")
            self.trackInvalidDroneMoves += 1
            return False

        yVal = self.drone.position.getY()
        yVal += int(y)
        if self.validateValY(yVal) is False:
            print("--INVALID Drone move, ERROR: Invalid Y move value for Drone results in Y =", yVal)
            self.trackInvalidDroneMoves += 1
            return False
        zVal = self.drone.position.getZ()
        zVal += int(z)
        if self.validateXZVal(zVal) is False:
            print("--INVALID Drone move, ERROR: Z value is beyond the edge of the globe.")
            self.trackInvalidDroneMoves += 1
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
                    return False
            elif (self.validateValY(yValCube) is False) or (self.globe.get(hashPosition(xVal,yValCube,zVal)) is not None):
                print("\nERROR: Bad Y value or occupied space for cube, Drone will not move. Occupied space: ",xVal,yValCube,zVal)
                self.trackInvalidCubeMoves += 1
                return False

        ## check that position is open for drone
        if self.globe.get(hashPosition(xVal,yVal,zVal)) is not None:
            print("\nERROR: occupied space, Drone will not move. Occupied space: ",xVal,yVal,zVal, )
            self.trackInvalidDroneMoves += 1
            return False

        print("++Valid Drone move to: ",xVal,yVal,zVal)#logging for reporting
        self.trackValidDroneMoves += 1
        ## finally move the drone
        #print("old drone pos:", self.drone.position.getPositionVals())
        self.globe.pop(self.drone.getKey(), None)
        self.drone.setPosition(xVal,yVal,zVal)
        self.globe[self.drone.getKey()] = self.drone
        #print("....new drone pos (from drone):", self.drone.position.getPositionVals())
        #print("....new drone pos confirmed (from globe):", self.globe.get(hashPosition(xVal,yVal,zVal)))

        if self.drone.hasCubeAttached() is True:
            print("--Drone has cube, moving cube to:",xVal,yValCube,zVal)
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

        #else: #remove prior jve
            #print("No cube")##remove prior jve

        return True

    def Attach(self):
        print("Drone attach")
        if self.drone.hasCubeAttached() is True:
            print("ERROR: Invalid Drone pickup, drone already has a cube")
            self.trackInvalidDronePickup += 1
            return False
        dronePos = self.drone.getPosition()

        # will have a cube if valid
        checkForCube = self.globe.get(hashPosition(int(dronePos.getX()), (int(dronePos.getY())-1), int(dronePos.getZ())))
        if checkForCube is None:
            print("ERROR: Invalid Drone pickup, no cube below Drone position:",dronePos.getX(),dronePos.getY(),dronePos.getZ())
            self.trackInvalidDronePickup += 1
            return False
        print("Color of P/U cube: ", checkForCube.cubeColor())
        #attach the cube to the drone
        attCube = Cube(int(dronePos.getX()), (int(dronePos.getY())-1), int(dronePos.getZ()), checkForCube.cubeColor())
        #print("attCube vals:", attCube.getKey(),attCube.cubeColor())
        self.drone.attachCube(attCube)
        self.trackValidDronePickup += 1

    def Release(self):
        print("Drone release")
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
                currY

        #print("Drone release Valid at 0 level")
        oldCube = self.drone.cubeObject()
        oldCubeKey = oldCube.getKey()
        self.globe.pop(oldCubeKey, None)
        dpCube = self.drone.dropCube(currY)#### need to watch this one should it be +1???? jve --- not right now************************************
        print("Dropped cube at:", dpCube.getPosition().getPositionVals(),", cube is:",dpCube.cubeColor(), currY)
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

    def printResults(self):
        print("*************************************************************")
        print("Results of the run:")
        print("Valid Drone Moves:",self.trackValidDroneMoves)
        print("Invalid Drone Moves:",self.trackInvalidDroneMoves)
        print("Valid Cube Moves:",self.trackValidCubeMoves)
        print("Invalid Cube Moves:",self.trackInvalidCubeMoves)
        print("Valid Drone pickups:", self.trackValidDronePickup)
        print("Invalid Drone pickups:", self.trackInvalidDronePickup)
        print("Valid Drone releases:", self.trackValidDroneRelease)
        print("Invalid Drone releases:", self.trackInvalidDroneRelease)
        print("*************************************************************")

    def validateXZVal(self, val):
        if int(val) < -50:
            return False
        elif int(val) > 50:
            return False
        return True

    def validateXZVal2(self, val):
        if val == '?':
            return 55

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
#############################################################
def hashPosition(x,y,z):
    checkPos = Position(x,y,z)
    return checkPos.__hash__()

def goalTestF(state, goal):
    return state == goal
################################################################
class JQueue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def put(self,x):
        #print("Frontier Adding", x)
        self.elements.append(x)

    def get(self):
        if len(self.elements) == 0:
            return None
        return self.elements.popleft()

def getNeighbors(currPos,tgtPos):
    #print("getNeighbors fm position:",currPos)
    (cpx,cpy,cpz) = currPos
    (tx,ty,tz) = tgtPos
    #these make up the preferred move
    mvX = 0
    mvY = 0
    mvZ = 0
    ## set possible moves based on this simple heuristic
    ## but this doesn't account for things in the way - need to add more moves
    ## This is the optimal move, so first, then the other simple moves will
    ## be calculated and ranked in the queue
    if int(cpx) < int(tx):
        mvX = 1
    elif int(cpx) > int(tx):
        mvX = -1
    if int(cpy) < int(ty):
        mvY = 1
    elif int(cpy) > int(ty):
        mvY = -1
    if int(cpz) < int(tz):
        mvZ = 1
    elif int(cpz) > int(tz):
        mvZ = -1

    print("neighborhood created optimal value is:", mvX,mvY,mvZ)

    queueToPass = qu.deque()
    priorQ = qu.PriorityQueue()
    valuesToSort = []

    #### make up the rest of the moves and rank them
        #### make up the rest of the moves and rank them
    mv1X = int(cpx)+1
    mv1Y = int(cpy)
    mv1Z = int(cpz)
    rank1 = calcDistRank(mv1X,mv1Y,mv1Z,tx,ty,tz)
    priorQ.put(rank1)
    valuesToSort.append((rank1,(mv1X,mv1Y,mv1Z)))

    mv2X = int(cpx)-1
    mv2Y = int(cpy)
    mv2Z = int(cpz)
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    ##X,Y
    mv2X = int(cpx)+1
    mv2Y = int(cpy)+1
    mv2Z = int(cpz)
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    mv2X = int(cpx)+1
    mv2Y = int(cpy)-1
    mv2Z = int(cpz)
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    mv2X = int(cpx)-1
    mv2Y = int(cpy)+1
    mv2Z = int(cpz)
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    mv2X = int(cpx)-1
    mv2Y = int(cpy)-1
    mv2Z = int(cpz)
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    ##X,Z
    mv2X = int(cpx)+1
    mv2Y = int(cpy)
    mv2Z = int(cpz)-1
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    mv2X = int(cpx)-1
    mv2Y = int(cpy)
    mv2Z = int(cpz)-1
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    mv2X = int(cpx)-1
    mv2Y = int(cpy)
    mv2Z = int(cpz)+1
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))
    mv2X = int(cpx)+1
    mv2Y = int(cpy)
    mv2Z = int(cpz)+1
    rank2 = calcDistRank(mv2X,mv2Y,mv2Z,tx,ty,tz)
    priorQ.put(rank2)
    valuesToSort.append((rank2,(mv2X,mv2Y,mv2Z)))

    mv3X = int(cpx)
    mv3Y = int(cpy)+1
    mv3Z = int(cpz)
    rank3 = calcDistRank(mv3X,mv3Y,mv3Z,tx,ty,tz)
    priorQ.put(rank3)
    valuesToSort.append((rank3,(mv3X,mv3Y,mv3Z)))

    mv4X = int(cpx)
    mv4Y = int(cpy)-1
    mv4Z = int(cpz)
    rank4 = calcDistRank(mv4X,mv4Y,mv4Z,tx,ty,tz)
    priorQ.put(rank1)
    valuesToSort.append((rank4,(mv4X,mv4Y,mv4Z)))
    ##YZ
    mv4X = int(cpx)
    mv4Y = int(cpy)+1
    mv4Z = int(cpz)-1
    rank4 = calcDistRank(mv4X,mv4Y,mv4Z,tx,ty,tz)
    priorQ.put(rank1)
    valuesToSort.append((rank4,(mv4X,mv4Y,mv4Z)))
    mv4X = int(cpx)
    mv4Y = int(cpy)-1
    mv4Z = int(cpz)-1
    rank4 = calcDistRank(mv4X,mv4Y,mv4Z,tx,ty,tz)
    priorQ.put(rank1)
    valuesToSort.append((rank4,(mv4X,mv4Y,mv4Z)))
    mv4X = int(cpx)
    mv4Y = int(cpy)-1
    mv4Z = int(cpz)+1
    rank4 = calcDistRank(mv4X,mv4Y,mv4Z,tx,ty,tz)
    priorQ.put(rank1)
    valuesToSort.append((rank4,(mv4X,mv4Y,mv4Z)))
    mv4X = int(cpx)
    mv4Y = int(cpy)+1
    mv4Z = int(cpz)+1
    rank4 = calcDistRank(mv4X,mv4Y,mv4Z,tx,ty,tz)
    priorQ.put(rank1)
    valuesToSort.append((rank4,(mv4X,mv4Y,mv4Z)))

    mv5X = int(cpx)
    mv5Y = int(cpy)
    mv5Z = int(cpz)+1
    rank5 = calcDistRank(mv5X,mv5Y,mv5Z,tx,ty,tz)
    priorQ.put(rank5)
    valuesToSort.append((rank5,(mv5X,mv5Y,mv5Z)))

    mv6X = int(cpx)
    mv6Y = int(cpy)
    mv6Z = int(cpz)-1
    rank6 = calcDistRank(mv6X,mv6Y,mv6Z,tx,ty,tz)
    priorQ.put(rank6)
    valuesToSort.append((rank6,(mv6X,mv6Y,mv6Z)))

    ## The triples
    mv7X = int(cpx)+1
    mv7Y = int(cpy)+1
    mv7Z = int(cpz)+1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)-1
    mv7Y = int(cpy)-1
    mv7Z = int(cpz)-1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)+1
    mv7Y = int(cpy)-1
    mv7Z = int(cpz)-1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)-1
    mv7Y = int(cpy)+1
    mv7Z = int(cpz)-1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)-1
    mv7Y = int(cpy)-1
    mv7Z = int(cpz)+1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)+1
    mv7Y = int(cpy)+1
    mv7Z = int(cpz)-1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)+1
    mv7Y = int(cpy)-1
    mv7Z = int(cpz)+1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))
    mv7X = int(cpx)-1
    mv7Y = int(cpy)+1
    mv7Z = int(cpz)+1
    rank7 = calcDistRank(mv7X,mv7Y,mv7Z,tx,ty,tz)
    priorQ.put(rank7)
    valuesToSort.append((rank7,(mv7X,mv7Y,mv7Z)))

    i = 0
    sz = 26
    while i < sz:
        spotV = priorQ.get()

        if len(valuesToSort) == 1:
            queueToPass.append(valuesToSort[0][1])
            break
        j = 0
        for item in valuesToSort:
            if item[0] == spotV:
                queueToPass.append(item[1])
                valuesToSort.pop(j)
                break
            j += 1
        i += 1

    ## put the priority move first
    queueToPass.appendleft((mvX,mvY,mvZ))
    print("neighborhood2")
    return queueToPass


def calcDistRank(newPosX,newPosY,newPosZ, tgtPosX,tgtPosY,tgtPosZ):
    return abs(int(newPosX)- int(tgtPosX)) + abs(int(newPosY) - int(tgtPosY)) + abs(int(newPosZ) - int(tgtPosZ))

### search for the position in ourWorld2
def simpleBreadthFirstSearch(wld1,wld2):
    targetPos = wld2.drone.currentPos().getPositionVals()
    (targx,targy,targz) = targetPos
    #print("target:",targetPos,targx,targy,targz)

    dronePos = wld1.drone.currentPos().getPositionVals()
    (drnx,drny,drnz) = dronePos
    #print("start:",dronePos,drnx,drny,drnz)
    frontier = JQueue()
    frontier.put(dronePos)
    #pathTo = []
    visited = {}
    visited[dronePos] = True
    loopctr = 0
    while True:
        current = frontier.get()
        #print("top of simpleBreadthFirstSearch loop - Visiting:", current)
        moveList = getNeighbors(current,targetPos)
        while True:
            mover = moveList.popleft()
            if mover == (0,0,0):
                print("*********Found position by calculation1")
                return
            if wld1.globe.keys() == wld2.globe.keys():
                print("****Found the position inside!")
                return
            (MvX,MvY,MvZ) = mover
            (drX,drY,drZ) = wld1.drone.currentPos().getPositionVals()
            newPosX = int(drX) + int(MvX)
            newPosY = int(drY) + int(MvY)
            newPosZ = int(drZ) + int(MvZ)

            #print("Mover is:", MvX,MvY,MvZ)
            #print("position to compare:", newPosX,newPosY,newPosZ)
            positionToCompare = (newPosX,newPosY,newPosZ)

            if positionToCompare not in visited:
                if wld1.move(MvX,MvY,MvZ) is False:
                    visited[positionToCompare] = True
                    print("blocked move")
                    continue
                else:
                    frontier.put(positionToCompare)
                    visited[positionToCompare] = True
                    pathOfAllMoves.append((newPosX,newPosY,newPosZ))
                    if wld1.globe.keys() == wld2.globe.keys():
                        print("****Found the position!")
                        return
                    break
            #else:
                #print("+++position is in visited", positionToCompare)
            loopctr += 1
    #return pathTo

def findCube(wld_1,color):
    #look through the initial world to find a cube
    cubeList = wld_1.state()
    rowFound = 0
    for cube in cubeList:
        (cubeI,cubeColor) = cubeList[cube].getPosition().getPositionVals(),cubeList[cube].cubeColor()
        #print("Cube is:", cubeI, cubeColor)
        #print("Wld_1 values", cubeList[cube].getPosition().getPositionVals(), ", color:", cubeList[cube].cubeColor())
        if cubeColor == color:
            print("color matched!", cubeColor)
            return cubeList[cube].getPosition().getPositionVals()
        rowFound += 1
    print("ERROR: cube of that color isn't in the world,", color)
    return None

## since the hashing for keys in the globe dictionary will resort the
## order the items come in, need to create a list of colors of cubes and
## go through them
def createListOfCubesToMoveByColor(inWld1):
    cubeList1 = inWld1.state()
    colorList = []
    #assuming the lists are of equal length
    for key in cubeList1:
        #print("vals2:", cubeList1[key].getPosition().getPositionVals(), ", color:", cubeList1[key].cubeColor())
        cubeLColor = cubeList1[key].cubeColor()
        if cubeLColor == 'drone':
            continue
        #print ("cubeLColor:", cubeLColor )
        colorList.append((cubeLColor,key))

    return colorList

def BFSToFindACube(wld_in,cPos):
    #print("BFSToFindACube")
    print("cPos is:", cPos)
    (cbTargx,cbTargy,cbTargz) = cPos

    cPosFind = cbTargx,(int(cbTargy)+1),cbTargz
    #print("cPosFind:",cbTargx,(int(cbTargy)+1),cbTargz)

    dronePos = wld_in.drone.currentPos().getPositionVals()
    (drnx,drny,drnz) = dronePos
    #print("start drone pos:",dronePos,drnx,drny,drnz)

    frontier = JQueue()
    frontier.put((drnx,drny,drnz))
    visited = {}
    #####path2 = []
    visited[dronePos] = True
    loopctr = 0

    while True: ## loopctr < 50:
        current = frontier.get()
        #if current is None:
        #    continue
        #print("top of BFSToFindACube loop - Visiting:", current)

        #only getting back a singular move
        moveList = getNeighbors(current,cPosFind)
        if moveList == None:
            print("Out of moves for this position:",current,cPosFind)
        while True:
            if len(moveList) == 0:
                break
            mover = moveList.popleft()
            #print("Mover value is:", mover)
            if mover == (0,0,0):
                print("*********Found position by calculation2")
                checker = False
                return
            if wld_in.drone.currentPos().getPositionVals() == cPosFind:
                print("****Found the position inside!")
                checker = False
                return
            (MvX,MvY,MvZ) = mover
            (drX,drY,drZ) = wld_in.drone.currentPos().getPositionVals()
            newPosX = int(drX) + int(MvX)
            newPosY = int(drY) + int(MvY)
            newPosZ = int(drZ) + int(MvZ)

            #print("Mover is:", MvX,MvY,MvZ)
            #print("position to compare:", newPosX,newPosY,newPosZ)
            positionToCompare = (newPosX,newPosY,newPosZ)

            if positionToCompare not in visited:
                if wld_in.move(MvX,MvY,MvZ) is False:
                    visited[positionToCompare] = True
                    print("==blocked move")
                    continue
                else:
                    frontier.put(positionToCompare)
                    visited[positionToCompare] = True
                    pathOfAllMoves.append((newPosX,newPosY,newPosZ))
                    if wld_in.drone.currentPos().getPositionVals() == cPosFind:
                        print("****Found the cube position!")
                        checker = False
                        return
                    break
            #else:
                #print("+++position is in visited", positionToCompare)
            loopctr += 1
    #return path2

if __name__ == "__main__":

    ##find a cube of a specified color and attach the drone to it
    ourWorld1 = DroneWorld("world1.txt")
    ourWorld2 = DroneWorld("world2.txt")
    start_time = time.time()

    if goalTestF(ourWorld1.state().keys(),ourWorld2.state().keys()) is True:
        elapsed_time = time.time() - start_time
        print("Search has already finished, states are equal. Total time: ",elapsed_time)
        exit()

    ## process the first world for all cube positions then compare to second world to determine
    ## what moves are needed
    ## also wild cards as "?" can be within the files indicating a cube is stuck somewhere
    ## on any level
    if len(ourWorld1.state().keys()) != len(ourWorld2.state().keys()):
        print("ERROR: The two worlds do not hold the same number of items and are invalid, Exiting...")
    numCubes = len(ourWorld1.state().keys())
    processedCubes = 0
    processedCubeList = []
    redoCubeList1 = []
    redoCubeList2 = []
    pathOfAllMoves = []

    file1 = open("world1.txt", 'r')
    file2 = open("world2.txt", 'r')
    loopctr = 0
    while True: ## loopctr < 8:
        #print("*********TOP")
        listVal_1 = file1.readline()
        if listVal_1 == '':
            #print("Done")
            break
        listVal_1 = listVal_1.strip()
        listVal_2 = file2.readline()
        listVal_2 = listVal_2.strip()
        print("listVal_1", listVal_1)
        print("listVal_2", listVal_2)
        if 'drone' in listVal_1:
            #print ("yep")
            continue
        values_1 = listVal_1.split(',')
        cube1 = Cube(int(values_1[0]),int(values_1[1]),int(values_1[2]),str(values_1[3]))
        values_2 = listVal_2.split(',')
        if str(values_2[0]) == '?' or str(values_2[2]) == '?':
            #print("Found a special one:", values_2)
            redoCubeList1.append(cube1)
            cubeS = Cube(55,int(values_2[1]),55,str(values_2[3]))
            #print("Special cube values:", cubeS)
            redoCubeList2.append(cubeS)
            continue

        cube2 = Cube(int(values_2[0]),int(values_2[1]),int(values_2[2]),str(values_2[3]))
        if cube1.getKey() == cube2.getKey():
            print("CubeMatch, no movement required; positions", cube1.getPosition().getPositionVals(), cube1.cubeColor())
            processedCubeList.append((cube1,True))
            continue
        else:
            print("Moving cube?:", cube1.getPosition().getPositionVals(), cube1.cubeColor())
            print("cube1 Y:", values_1[1], "Cube2 Y:",int(values_2[1]), "Plus1", int(values_2[1])+1)
            ## this
            if int(values_1[1]) != (int(values_2[1])):
                print("========Adding cube2 to later list:")
                redoCubeList1.append(cube1)
                redoCubeList2.append(cube2)
            else:
                BFSToFindACube(ourWorld1,cube1.getPosition().getPositionVals())
                ourWorld1.Attach()
                BFSToFindACube(ourWorld1,cube2.getPosition().getPositionVals())
                ourWorld1.Release()
                processedCubeList.append((cube1,True))

        loopctr += 1

    file1.close()
    file2.close()

    ## now to move those that were above it all
    cubeMatchNo = 0
    print("$$$$$$$$$$$$$ Starting REDO LIST $$$$$$$$$$$$$$$$")
    while True:
        print("==============================================================================================")
        print("####TOP2 ####")
        for cubeM1 in redoCubeList1:
            print("==============================================================================================")
            print("redo1:", cubeM1.getPosition().getPositionVals(), cubeM1.cubeColor())
            print("current Y position??", cubeM1.getPosition().getPositionVals()[1])

            cubeM2 = redoCubeList2[cubeMatchNo]
            print("CubeM2 is:", cubeM2.cubeColor(), cubeM2.getPosition().getPositionVals(), cubeM2.getPosition().getPositionVals()[0])
            if int(cubeM2.getPosition().getPositionVals()[0]) != 55:
                print("-------------Processing regular on redo---------------")
                BFSToFindACube(ourWorld1,cubeM1.getPosition().getPositionVals())##################################
                ourWorld1.Attach()
                BFSToFindACube(ourWorld1,cubeM2.getPosition().getPositionVals())###################################
                ourWorld1.Release()
                processedCubeList.append((cubeM1,True))
            else:
                # first find a stack that is high enough, so search through world2 list for a qualified stack
                print("the else")
                file2R = open("world2.txt", 'r')
                while True:
                    print("##### top3#############")
                    listVal_2R = file2R.readline()
                    listVal_2R = listVal_2R.strip()
                    if 'drone' in listVal_2R:
                        print ("yep2")
                        continue
                    values_2R = listVal_2R.split(',') ### problem - if multiple q's finds othe q and uses it
                    if '?' in values_2R:
                        continue
                    print("values_2R",values_2R)
                    if int(values_2R[1]) == int(cubeM2.getPosition().getPositionVals()[1])-1:
                        cubeDest = Cube(int(values_2R[0]),(int(values_2R[1])+1),int(values_2R[2]),str(values_2R[3]))
                        print("-------------Processing regular on redo2---------------")
                        BFSToFindACube(ourWorld1,cubeM1.getPosition().getPositionVals())##################################
                        ourWorld1.Attach()
                        BFSToFindACube(ourWorld1,cubeDest.getPosition().getPositionVals())##############################
                        ourWorld1.Release()
                        processedCubeList.append((cubeM1,True))
                        #ourWorld2.state().pop(cubeM2.getKey())
                        break
            cubeMatchNo +=1
        break
    print("==============================================================================================")
    simpleBreadthFirstSearch(ourWorld1,ourWorld2) ##put the drone away  ###############################################


    #print("\n\nprocessedCubeList", processedCubeList)
    #i = 0
    #while i < len(redoCubeList2):
    #    print("redoCubeList", redoCubeList2[i].getPosition().getPositionVals(), redoCubeList2[i].cubeColor())
    #    i +=1
    print("\n==================== MOVES ==========================================================================")
    fileOut = open("Paths.txt","w")
    pmLen = len(pathOfAllMoves)
    i = 1
    print("Number of moves mode by the drone:", pmLen)
    for pos in pathOfAllMoves:
        fileOut.write(str(pos))
        if i < pmLen:
            fileOut.write(",")
        #print("Move list:",pos, i)
        i += 1
    fileOut.close()

    #print("====================processedCubeList==========================================================================")
    #for item in processedCubeList:
    #    print("processedCubeList:", item[0].getPosition().getPositionVals(), item[0].cubeColor(),item[1])

    print("\n++++++++++++ DATA +++++++++++++")
    print("VERIFY final cube positions to world 2 values:")
    for key in ourWorld1.state():
        print("cube:", ourWorld1.state()[key].getPosition().getPositionVals(), ", color:", ourWorld1.state()[key].cubeColor())
    ################ TIMING #################
    ourWorld1.printResults()
    elapsed_time = time.time() - start_time
    print("Total time: ",elapsed_time)