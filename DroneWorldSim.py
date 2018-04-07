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
#############################################################
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

    def toString(self):
        rtnStr = "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"
        return rtnStr

###############################################################################################
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

    def toString(self):
        strTRtn = "Cube: Color: " + self.color + ", Pos: " + str(self.getPosition().getPositionVals())
        return strTRtn

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
        print("++Attached cube (to drone), cube vals:", cube.getPosition().toString(),cube.cubeColor())
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
        self.specialCubes = []
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
        self.specialIdentifier = 55

        for line in self.worldFill:
            state = False
            specialPos = False
            line = line.strip()
            values = line.split(' ')
            print("Line Values: ", line)
            #print("values---: ", values)
            #print("===Size of values array:", len(values))

            ## To handle extra spaces in a line of text
            ind = 0
            hold = 0
            sizeVals = len(values)
            if sizeVals > 4:
                holdVal = values
                while ind < sizeVals:
                    if len(holdVal[ind]) > 0:
                        #print("Good value:", holdVal[ind])
                        values[hold] = holdVal[ind]
                        hold += 1
                    ind += 1
                #print("++The 4 important values:", values[0],values[1],values[2],values[3])

            ## For special position characters
            if values[0] == '?' or values[1] == '?' or values[2] == '?':
                state = True
                if values[0] == '?':
                    values[0] = int(self.specialIdentifier)
                if values[1] == '?':
                    values[1] = int(self.specialIdentifier)
                if values[2] == '?':
                    values[2] = int(self.specialIdentifier)
                self.specialIdentifier += 1
                specialPos = True
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

            #print("++Values:" + str(values[0]) + ", " + str(values[1]) + ", " + str(values[2])+ ", " + str(values[3]))
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

                    if specialPos is True:
                        self.specialCubes.append(cubeRtn)
        if not self.droneAccountedFor:
            print("#####################################################")
            print("WARNING, No Drone has been passed into the simulation\n")
            print("#####################################################")

        #print("size of special list:" , len(self.specialCubes))
        #for cube in self.specialCubes:
        #    print("cube values:", cube.getPosition().toString(), cube.cubeColor())

    #####################################################
    def processList(self, inList, floatList):
        for entry in inList:
            self.globe[entry.getKey()] = entry # Add the position to the globe

        ##Looking for a cube that's floating, checking for something below it to verify
        for floater in floatList:
            tstX = floater.getPosition().getX()
            tstY = floater.getPosition().getY()
            tstZ = floater.getPosition().getZ()
            ## looking for special condition of ('?','?','?',color)
            if tstX >= 55 or tstZ >= 55 or tstY >= 55:
                #print("****special '?' case found****")
                self.globe[floater.getKey()] = floater # Add the position to the globe
                continue

            tmpKey = hashPosition(int(tstX),(int(tstY)-1),int(tstZ))
            if self.globe.get(tmpKey) is None:
                print("Floater Found:", self.globe.get(floater.getKey()))
                print("ERROR: Cube is floating in space, invalid cube Y position",floater.getPosition().getPositionVals(), floater.cubeColor())
                continue
            else:
                self.globe[floater.getKey()] = floater # Add the position to the globe

    #####################################################
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
        ## Y move value has already been verified above
        if self.drone.hasCubeAttached():
            if self.validateValY(yValCube) is True:
                if self.globe.get(hashPosition(xVal,yValCube,zVal)) is not None:
                    if (self.globe.get(hashPosition(xVal,yValCube,zVal)).cubeColor()) is not 'drone':
                        print("\nERROR: Bad Y value or occupied space for cube, Drone will not move. Occupied space: ",xVal,yValCube,zVal)
                        self.trackInvalidCubeMoves += 1
                        return False

        ## check that position is open for drone
        if self.globe.get(hashPosition(xVal,yVal,zVal)) is not None:
            if self.globe.get(hashPosition(xVal,yVal,zVal)).cubeColor() is not 'drone':
                print("\nERROR: occupied space, Drone will not move. Occupied space: ",xVal,yVal,zVal, )
                self.trackInvalidDroneMoves += 1
                return False

        print("++Valid Drone move to: ",xVal,yVal,zVal)#logging for reporting
        self.trackValidDroneMoves += 1
        #print("\nDrone world state before----")
        #self.Speak()
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
            #print("Drone world state after----")
            #self.Speak()

        return True

    #####################################################
    def Attach(self):
        print("---Drone attach")
        if self.drone.hasCubeAttached() is True:
            print("ERROR: Invalid Drone pickup, drone already has a cube")
            self.trackInvalidDronePickup += 1
            return False
        dronePos = self.drone.getPosition()

        # will be a cube if valid, look just below the drone
        checkForCube = self.globe.get(hashPosition(int(dronePos.getX()), (int(dronePos.getY())-1), int(dronePos.getZ())))
        if checkForCube is None:
            print("ERROR: Invalid Drone pickup, no cube below Drone position:",dronePos.getX(),dronePos.getY(),dronePos.getZ())
            self.trackInvalidDronePickup += 1
            return False
        print("Color of P/U cube: ", checkForCube.cubeColor())
        #attach the cube to the drone
        attCube = Cube(int(dronePos.getX()), (int(dronePos.getY())-1), int(dronePos.getZ()), checkForCube.cubeColor())
        print("attCube vals:", attCube.getPosition().toString(),attCube.cubeColor())
        self.drone.attachCube(attCube)
        self.trackValidDronePickup += 1
        print("---Drone attach - done")

    #####################################################
    def Release(self):
        print("\n========Drone release====start======")
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
            tmpKey = hashPosition(drnX,(currY-1), drnZ)##spot below the cube
            #print("Current cube position values:",drnX,currY, drnZ)
            #print("--info--The space below the cube occupied?:",self.globe.get(tmpKey).getPosition().toString(),\
            #               "color:", self.globe.get(tmpKey).cubeColor())

            #drop from a height above a stack
            while (self.globe.get(tmpKey) is None) and (currY > -1):
                print("--in While--The space occupied?:",self.globe.get(tmpKey).getPosition().toString() )
                currY -= 1 ## next spot down
                tmpKey = hashPosition(drnX,currY,drnZ)
                #print("Dropping down, determining Y for release:",currY)


        #print("Drone release Valid at 0 level")
        oldCube = self.drone.cubeObject()
        oldCubeKey = oldCube.getKey()
        self.globe.pop(oldCubeKey, None)#remove old cube key
        dpCube = self.drone.dropCube(currY)#create new cube to put into correct position
        print("Dropped cube at:", dpCube.getPosition().getPositionVals(),", cube is:",dpCube.cubeColor(), "currY is:",currY)
        self.globe[dpCube.getKey()] = dpCube #put the cube in the world
        self.trackValidDroneRelease += 1
        print("========Drone release=====done=====")

    #####################################################################
    def Speak(self):
        print("\n++++++++++++++++++++++++++ State DATA +++++++++++++++++++++++++++++++")
        for key in self.globe:
            if self.state()[key].cubeColor() == "drone":
                print("drone:", self.globe[key].getPosition().getPositionVals())
            else:
                print(" cube:", self.globe[key].getPosition().getPositionVals(), self.globe[key].cubeColor())
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


    def state(self):
        return self.globe

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

################################################################################################################
##################### End of Cube World simulation code
################################################################################################################
