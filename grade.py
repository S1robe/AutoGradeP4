#!/bin/python

import os.path
import sys
import re
import subprocess as subp
import time


passBCorrectMsg = "Thread {thNum}: Wooh! I'm about to ride the roller coaster for the {tNum} time! I have {iNum} " \
                  "iterations left."
passECorrectMsg = "thread {thNum}: Completed {iNum} iterations on the roller coaster. Exiting."
rideBCorrectMsg = "Car: {pNum} {cPass} riding the roller coaster. Off we go on the {rNum} ride!"
rideCCorrectMsg = "Car: ride {rNum} completed."
progECorrect = "Car: Roller coaster shutting down."

passBoardMsg = "(Thread $x: Wooh! I.m about to ride the roller coaster for the (?:(?:(?:[1-9]|[1-9]+[0-9]*0)*1 ?st)|(" \
               "?:(?:[1-9]|[1-9]+[0-9]*0)*2 ?nd)|(?:(?:[1-9]|[1-9]+[0-9]*0)*3 ?rd)|(?:(?:[1-9]|[1-9]+[0-9]*0)*[4-9] " \
               "?th)) time! I have (?:[1-9]|[1-9]+[0-9]*0)*[0-9] iterations left\\.)"
passExitMsg = "([Tt]hread $x: Completed (?:[1-9]|[1-9]+[0-9]*0)*[0-9] iterations? on the roller coaster\\. " \
              "Exiting\\.)"
rideBeginMsg = "(Car: (?:[1-9]|[1-9]+[0-9]*0)*[0-9] passenger(?: is|s are) riding the roller coaster\\. Off we go on " \
               "the (?:[1-9]|[1-9]+[0-9]*0)*[0-9] ride!)"
rideCompleteMsg = "(Car:  ?ride (?:[1-9]|[1-9]+[0-9]*0)*[0-9]  ?completed\\.)"
progExit = "(Car: Roller coaster shutting down\\.)"

ordinals = {0: "th", 1: "st", 2: "nd", 3: "rd", 4: "th", 5: "th", 6: "th", 7: "th", 8: "th", 9: "th"}
numIterations = {int: int}
passBoardMsgs = {int: list}
passCompleteMsgs = {int: list}
rBegMsgs = list()
rEndMsgs = list()
progEMsg = list()
pout = 0


# finds all matching strings according to @refPattern
def getOutput(refPattern: str, output: str):
    return re.findall(refPattern, output, flags=re.IGNORECASE)


# attempt to extract iterations from the exit strings
def getIterNorm(string: str):
    sub = re.findall("((?:[1-9]|[1-9]+[0-9]*0)*[0-9]) iterations", string)
    return int(sub[0])


# Attempt to extract iterations from the (#)st/nd/rd/ ... time! .....
def getIterSpec(string: str):
    sub = re.findall("((?:[1-9]|[1-9]+[0-9]*0)*[0-9]).?(?:st|nd|rd|th)", string)
    return int(sub[0])


# Just stacks output messages
def pretty(top: list, bot: list):
    longer = max(len(top), len(bot))
    for e in range(longer):
        if e < len(top):
            print(top[e])
        if e < len(bot):
            print(bot[e])


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
    if isExec:
        pout = subp.check_output(args, text=True)
    else:
        pout = "".join(open(filename, "r").readlines())
        # globally assigned
    rBegMsgs = getOutput(rideBeginMsg, pout)
    rEndMsgs = getOutput(rideCompleteMsg, pout)
    progEMsg = getOutput(progExit, pout)

    for x in range(n):
        numIterations[x] = "(#)"
        passCompleteMsgs[x] = getOutput(passExitMsg.replace("$x", str(x)), pout)  # count exit times
        passBoardMsgs[x] = getOutput(passBoardMsg.replace("$x", str(x)), pout)  # Matches passenger get on the coaster

        if len(passCompleteMsgs[x]) > 1:  # exit more than once, fail
            pretty(passCompleteMsgs[x], [])
            print("Passenger", x, "exited more than once!")
            exit(1)
        elif len(passCompleteMsgs[x]) == 0:  # need exactly 1 complete message
            # attempt to get iterations from the boarding messages
            if len(passBoardMsgs[x]) != 0:
                numIterations[x] = getIterSpec(passBoardMsgs[x][len(passBoardMsgs[x]) - 1])  # check last
            else:
                badBegStrings = set(re.findall("(T.*{x}:.*W.*\\.)".format(x=x), pout))
                badBegStrings.difference_update(set(passBoardMsgs[x]))  # remove good ones from the found ones
                badBegStrings = list(badBegStrings)  # should only be the bad strings
                if len(badBegStrings) == 0:
                    badBegStrings = ["They may exist, but are too malformed, test locally."]

                badEndStrings = set(re.findall("([Tt].*{x}:.*Completed.*\\.)".format(x=x), pout))
                badEndStrings.difference_update(passCompleteMsgs[x])  # remove good ones from the found ones
                badEndStrings = list(badEndStrings)  # should only be the bad strings
                if len(badEndStrings) == 0:
                    badEndStrings = ["They exist, but too malformed, test locally."]

                print("Unable to match Passenger Boarding or Exiting!",
                      "\n\nExpecting Beginnings Like:\n", passBCorrectMsg.format(thNum=x, tNum="(#)(st|nd|rd|th)", iNum="(#)"),
                      "\nBad Beginnings:\n",
                      "\n".join(badBegStrings),
                      "\n\nExpecting Ends Like:\n", passECorrectMsg.format(thNum=x, iNum="(#)"),
                      "\nBad Endings:\n",
                      "\n".join(badEndStrings))

                exit(1)
        else:
            # attempt to get iterations from the exit messages
            numIterations[x] = getIterNorm(passCompleteMsgs[x][0])

        # if boarding doesn't match what you said you did
        if len(passBoardMsgs[x]) != numIterations[x]:
            badBegStrings = re.findall("(T.*{x}:.*W.*\\.)".format(x=x), pout)
            if len(badBegStrings) == 0:
                badBegStrings = ["They may exist, but are too malformed, test locally."]

            print("Passenger", x, "claims they rode:", numIterations[x],
                  "\nExpecting Beginnings Like:\n", passBCorrectMsg.format(thNum=x, tNum="(#)(st|nd|rd|th)", iNum="(#)"),
                  "\nFound:\n",
                  "\n".join(badBegStrings))
            exit(1)

    rBegCnt = len(getOutput(rideBeginMsg, pout))
    rEndCnt = len(getOutput(rideCompleteMsg, pout))
    if rBegCnt != rEndCnt:
        # Attempt to find all ride beginning numbers/messages from the "good" ones
        foundRides = sorted(re.findall("(.*(?:[1-9]|[1-9]+[0-9]*0)*[0-9] ride.*)", "\n".join(rBegMsgs)))
        # Attempt ot find all ride end numbers/messages from the "good" ones
        foundEndRides = sorted(re.findall("(.*ride (?:[1-9]|[1-9]+[0-9]*0)*[0-9].*)", "\n".join(rEndMsgs)))

        print("Found Rides: (These are not in order)")
        pretty(foundRides, foundEndRides)

        print("Uneven amount of rides to ride endings!",
              "\n\nExpecting Beginnings Like: \n", rideBCorrectMsg.format(pNum="(#)", cPass="passenger(s are| is)", rNum="(#)"),
              "\n\nExpecting Ends Like: \n", rideCCorrectMsg.format(rNum="(#)"))

        exit(1)

    # if no or more than 1 exit message.
    if len(progEMsg) != 1:
        # loosely find the exit message
        progEMsg = re.findall("(.*shut.*\\.)", pout)
        if len(progEMsg) == 0:
            print("Missing:", progECorrect)
        else:
            print("Expected:", progECorrect,
                  "\nGot:     ", progEMsg[0])

        exit(1)

except subp.CalledProcessError as rProcess:  # returned process
    # Process returned non-zero error code
    if len(rProcess.stderr) != 0:
        print("You wrote to stderr (2), you should be writing to stdout (0)\n",
              "If you didnt write the following, then disregard this:",
              rProcess.stderr)

    if rProcess.returncode == -11:
        print("Something has gone horribly wrong! (Probably a Segfault)")
    else:
        print("Unknown Signal Error Code: ", rProcess.returncode)

    exit(1)

except OSError as oErr:
    print("File could not be read for testing ", filename, " :(")
    exit(1)

print("All test passed!")
exit(0)
