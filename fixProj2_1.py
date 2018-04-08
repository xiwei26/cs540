    def processList(self, inList, floatList):
        for entry in inList:
            self.globe[entry.getKey()] = entry # Add the position to the globe
        tmpRemoveList = []
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
                print("ERROR: Cube is floating in space, will retry, invalid cube Y position",floater.toString(), floater.cubeColor())
                continue
            else:
                self.globe[floater.getKey()] = floater # Add the position to the globe
                tmpRemoveList.append(floater)

        ## remove those that have been set
        for cube in tmpRemoveList:
            floatList.remove(cube)

        del tmpRemoveList[:]

        ## look again to see if there is now something below these or if there's one within the list
        if len(floatList) > 0:
            for floater2 in floatList:
                print("Looking at floater:", floater2.toString())
                tstX = floater2.getPosition().getX()
                tstY = floater2.getPosition().getY()
                tstZ = floater2.getPosition().getZ()
                tmpY = int(tstY)-1
                tmpKey = hashPosition(int(tstX),(int(tmpY)),int(tstZ))
                if self.globe.get(tmpKey) is not None:
                    print("Floater Base Found:") ##, (Cube)(self.globe.get(floater2.getKey())).getPosition())
                    self.globe[floater2.getKey()] = floater2 # Add the position to the globe
                    tmpRemoveList.append(floater2)
                    continue

                #see if there is one below
                for cubeT in floatList:
                    if cubeT.getPosition().getX() == tstX and cubeT.getPosition().getY()+1 == tstY and cubeT.getPosition().getZ() == tstZ:
                        self.globe[floater2.getKey()] = floater2
                        tmpRemoveList.append(floater2)
                        break

        ## remove those that have been set
        for cube in tmpRemoveList:
            floatList.remove(cube)
        del tmpRemoveList[:]