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

    #print("neighborhood created optimal value is:", mvX,mvY,mvZ)

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
    i = 0
    sz = 7
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

    return queueToPass
