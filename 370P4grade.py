#!/bin/python

import os.path
import sys
import re
import subprocess as subp

passBCorrectMsg = "Thread {thNum}: Wooh! I'm about to ride the roller coaster for the {tNum} time! I have {iNum} iterations left."
passECorrectMsg = "(T|t)hread {thNum}: Completed {iNum} iterations on the roller coaster. Exiting."
rideBCorrectMsg = "Car: {pNum} {cPass} riding the roller coaster. Off we go on the {rNum} ride!"
rideCCorrectMsg = "Car: ride {rNum} completed."
progECorrect = "Car: Roller coaster shutting down."

passBoardMsg = "(Thread $x: Wooh! I.m about to ride the roller coaster for the (?:(?:([1-9]|[1-9]+[0-9]*0)*1 ?st)|(?:(?:[1-9]|[1-9]+[0-9]*0)*2 ?nd)|(?:(?:[1-9]|[1-9]+[0-9]*0)*3 ?rd)|(?:(?:[1-9]|[1-9]+[0-9]*0)*[4-9] ?th)) time! I have (?:[1-9]|[1-9]+[0-9]*0)*[1-9] iterations left\\.)"
passExitMsg = "(hread $x: Completed (?:[1-9]|[1-9]+[0-9]*0)*[1-9] iterations? on the roller coaster\\. Exiting\\.)"
rideBeginMsg = "(Car: (?:[1-9]|[1-9]+[0-9]*0)*[0-9] passenger(?: is|s are) riding the roller coaster\\. Off we go on the (?:[1-9]|[1-9]+[0-9]*0)*[1-9] ride!)"
rideCompleteMsg = "(Car:  ?ride (?:[1-9]|[1-9]+[0-9]*0)*[1-9]  ?completed\\.)"
progExit = "(Car: Roller coaster shutting down\\.)"

ordinals = {0: "th", 1: "st", 2: "nd", 3: "rd", 4: "th", 5: "th", 6: "th", 7: "th", 8: "th", 9: "th"}

numIterations = {}
passBoardMsgs = {}
passCompleteMsgs = {}
rBegMsgs = list()
rEndMsgs = list()
progEMsg = list()


def handleBadThreads(tNum: int, errTypes: list):
    for e in errTypes:
        if e == 1:
            fixOutput(pout, passBoardMsgs[tNum], 1, tNum, numIterations[tNum])
        else:
            fixOutput(pout, passCompleteMsgs[tNum], 2, tNum, "#")


def fixOutput(badoutput: str, good: list, msg: int, theNum: int, eIter):
    if msg == 1:  # Fix the board messages
        badStrings = re.findall("(.*{x}:.*W.*)".format(x=theNum), badoutput)  # get all strings that have this
        if len(badStrings) == 0:
            print("Passenger", theNum, "is missing \"Wooh!\"")
            print("Expected something like: ",
                  passBCorrectMsg.format(thNum=theNum, tNum="(#) (st|nd|rd|th)", iNum="(#)"))
            return

        badStrings = set(badStrings)
        badStrings.difference_update(set(good))  # remove good ones from the found ones
        badStrings = list(badStrings)  # should only be the bad strings
        neededIters = []

        foundIters = re.findall("((?:[1-9]|[1-9]+[0-9]*0)*[1-9]) iterations", "".join(good))
        if len(foundIters) == 0:  # no iterations printed
            for e in range(eIter+1):
                neededIters.append(e)


        for st in badStrings:
            teNum = re.findall(".*((?:[1-9]|[1-9]+[0-9]*0)*[1-9]) (?:st|nd|rd|th).*", st)
            if len(teNum) == 0:
                teNum = "(#) (st|nd|rd|th)"
            else:
                teNum = int(teNum[0])
                teNum = "{x} {ord}".format(x=teNum, ord=ordinals[teNum % 10])

            eyeNum = neededIters.pop()
            correctOut = passBCorrectMsg.format(thNum=theNum, iNum=eyeNum, tNum=teNum)

            print("Expected: ", correctOut, "\nGot:     ", st)
    elif msg == 2:  # Fix the Exit messages
        badStrings = re.findall("(.*{x}:.*Completed.*)".format(x=theNum), badoutput)  # get all strings that have this
        if len(badStrings) == 0:
            print("Passenger", theNum, "is missing \"Completed\"")
            print("Expected something like: ",
                  passECorrectMsg.format(thNum=theNum, iNum="(#)"))
            return
        badStrings = set(badStrings)
        badStrings.difference_update(good)  # remove good ones from the found ones
        badStrings = list(badStrings)  # should only be the bad strings
        for st in badStrings:
            eyeNum = re.findall("((?:[1-9]|[1-9]+[0-9]*0)*[1-9]) iterations", st)
            if len(eyeNum) != 0:
                correctOut = passECorrectMsg.format(thNum=theNum, iNum=eyeNum[0])
            else:
                correctOut = passECorrectMsg.format(thNum=theNum, iNum=eIter)
            print("Expected: ", correctOut, "\nGot:     ", st)
    elif msg == 3:  # fix the Ride begin messages
        badStrings = re.findall("(.*passenger.*)".format(x=theNum), badoutput)  # get all strings that have this
        if len(badStrings) == 0:
            print("Missing \"passenger!\" in one or more Car begin messages")
            print("Expecting something like: ",
                  rideBCorrectMsg.format(pNum="(#)", cPass="passenger(s are| is)", rNum="(#)"))
            return
        badStrings = set(badStrings)
        badStrings.difference_update(good)  # remove good ones from the found ones
        badStrings = list(badStrings)  # should only be the bad strings
        for st in badStrings:
            pNum = re.findall("Car: ((?:[1-9]|[1-9]+[0-9]*0)*[0-9])", badoutput)
            cPass = "passenger"
            if len(pNum) == 0:
                cPass = "(#) passenger(s are| is)"
            else:
                pNum = int(pNum[0])
                if pNum == 1:
                    cPass = "passenger is"
                else:
                    cPass = "passengers are"

            rNum = re.findall("((?:[1-9]|[1-9]+[0-9]*0)*[1-9]) ride!", st)
            if len(rNum) == 0:
                rNum = "(#)"
            else:
                rNum = int(rNum[0])

            correctOut = rideBCorrectMsg.format(pNum=pNum, cPass=cPass, rNum=rNum)
            print("Expected: ", correctOut, "\nGot:     ", st)


def pretty(top: list, bot: list):
    longer = max(len(top), len(bot))
    for e in range(longer):
        if e < len(top):
            print(top[e])
        if e < len(bot):
            print(bot[e])


# finds all matching strings according to @refPattern
def getOutput(refPattern: str, outp: str):
    return re.findall(refPattern, outp, flags=re.IGNORECASE)


def getNumIterations(exitStr: str):
    sub = re.findall("((?:[1-9]|[1-9]+[0-9]*0)*[1-9]) iterations", exitStr)
    return int(sub[0])


argc = len(sys.argv)
if argc < 2:
    print("Usage: ./grade <filename (txt or exe)> <# n> <# c> <# i>")
    exit(1)

filename = sys.argv[1]  # this script will run the provided named
n = int(sys.argv[2])
c = int(sys.argv[3])
i = int(sys.argv[4])

if os.path.exists("./" + filename):
    filename = "./" + filename
elif os.path.exists(filename):
    pass
else:
    print("Cant find ", filename)
    exit(1)

args = list([filename, "-n", str(n), "-c", str(c), "-i", str(i)])
isExec = os.access(filename, os.X_OK)

try:
    pout = ""
    if isExec:
        pout = subp.check_output(args, text=True)
    else:
        pout = "".join(open(filename, "r").readlines())

    rideLim = 0
    if (n * i) % c == 0:
        rideLim = int(((n * i) / c) + c)
    else:
        rideLim = int(((n * i) / c) + (c - ((n * i) % c)))
    # n*i "people" to serve, with c seats, therefore (n*i)/c rides,
    # + i for the average amt of times it runs < than c
    rBegMsgs = getOutput(rideBeginMsg, pout)
    rEndMsgs = getOutput(rideCompleteMsg, pout)
    progEMsg = getOutput(progExit, pout)

    # pair tNum : error type(1|2)
    badThreads = []
    errorTypes = {int: []}

    for x in range(n):
        passCompleteMsgs[x] = getOutput(passExitMsg.replace("$x", str(x)), pout)  # count exit times
        if len(passCompleteMsgs[x]) > 1:
            pretty(passCompleteMsgs[x], [])
            print("Passenger", x, "exited more than once!")
            exit(1)

        elif len(passCompleteMsgs[x]) == 0:
            badThreads.append(x)
            errorTypes[x] = [2]

        if x >= len(numIterations):
            numIterations[x] = "(#)"
        if len(passCompleteMsgs) != 0:
            numIterations[x] = getNumIterations(
                passCompleteMsgs[x][0])  # Returns the choice from the random variable (0, i)

        good = getOutput(passBoardMsg.replace("$x", str(x)), pout)
        passBoardMsgs[x] = good  # Matches all times the passenger gets on the coaster

        if len(passBoardMsgs[x]) != numIterations[x]:
            if x not in badThreads:
                badThreads.append(x)
                errorTypes[x] = [1]
            else:
                errorTypes[x] = [1, 2]

    for t in badThreads:
        print("\nIssues with Passenger:", t, "-----")
        handleBadThreads(t, errorTypes[t])
        print("---- End Issues For Passenger:", t)

    rBegCnt = len(rBegMsgs)
    if not (0 <= rBegCnt <= rideLim):
        fixOutput(pout, rBegMsgs, 3, 0, 0)
        print("Invalid amount of rides possible.\n", "Expected <= ", rideLim, "\nGot: ", rBegCnt)
        exit(1)

    rEndCnt = len(rEndMsgs)
    if rBegCnt > rEndCnt:
        pretty(rBegMsgs, rEndMsgs)
        print("A ride never stopped with passengers on it!")
        exit(1)
    elif rBegCnt < rEndCnt:
        pretty(rBegMsgs, rEndMsgs)
        print("A ride ended before it began!")
        exit(1)
    if len(progEMsg) != 1:
        print("Expected to find: \n", progECorrect, "\nGot: ", progEMsg)
        # print("The ride never shutdown!")
        exit(1)

    if len(badThreads) != 0:
        exit(1)

except subp.CalledProcessError as rproc:  # returned process
    # Process returned non-zero error code
    print("Something has gone horribly wrong!")
    exit(1)

except OSError as oerr:
    print("File could not be read for testing ", filename, " :(")
    exit(1)
print("All test passed!")
exit(0)
