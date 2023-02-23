import re
import sys
import subprocess as subp

# <editor-fold desc="Output Messages Declaration">
passBoardStr = "(Thread {i}: Wooh! I’m about to ride the roller coaster for the (?:(?=1st)|(?=2nd)|(?=3rd)|(?=[1-9]+th)) time! I have [1-9]+ iterations left\\.)"
carBeginMsg = "(Car: (?:(?=0)|(?=[1-9]+) passengers are riding the roller coaster\\. Off we go on the [1-9]+[0-9]* ride!))"
rideMsg = "(Car: ride [1-9]+[0-9]* completed\\.)"
# </editor-fold>
# <editor-fold desc="Err Messages Declaration">
Usage = "Usage: -n <count> -c <count> -i <count>"
invalidNorC = "n (>c ) and n (<= 100) arguments required."
invalidValue = "./roller: invalid value - {badVal}."
invalidOption = "./roller: invalid option - {badVal}."
invalidI = "i (<= 20) required."
errMsg = ""


# </editor-fold>

# <editor-fold desc="Used Functions">
# finds all matching strings according to @refPattern
def getOutput(refPattern: str, outp: str):
    return re.findall(refPattern, outp)
# </editor-fold>

# <editor-fold desc="Beginning Init">
nOpt, n, cOpt, c, iOpt, i = "", "", "", "", "", ""
argc = len(sys.argv)
if argc < 2:
    print("Usage: ./AutoGrader.py <executable to run> [passedArg1] [pArg2] ....")
    exit(1)
filename = sys.argv[1]  # this script will run the provided named
if argc >= 8:
    passedArgs = sys.argv[2:]  # subset off the rest as passed arguments
    nOpt, n, cOpt, c, iOpt, i = passedArgs[2], passedArgs[3], passedArgs[4], passedArgs[5], passedArgs[6], passedArgs[7]
# </editor-fold>

# <editor-fold desc="Simple Args">
# 0  : this file name
# 1  : Passed Executable to run as subprocess
# 2+ : Passed Arguments to subprocess
# </editor-fold>
# <editor-fold desc="Detailed Args">
# 2(3)  : "-n" -> (String) The Passengers Option
# 3(4)  : "#"  -> (int)    The # of Passengers (Threads)
# 4(5)  : "-c" -> (String) The Passengers per car Option
# 5(6)  : "#"  -> (int)    The # of Passengers per car (Limit)
# 6(7)  : "-i" -> (String) The max Iterations per Customer Option
# 7(8)  : "#"  -> (int)    The # Limit for max Iterations per Customer
# </editor-fold>

# <editor-fold desc="Passed Argument Validation">
if argc < 3:
    errMsg = Usage
else:
    if nOpt != "-n":
        errMsg = str.format(invalidOption, badVal=nOpt[1:])  # format the error message as we would expect it!
    else:
        try:
            n = int(n)
            if not (0 < n <= 100):
                errMsg = invalidNorC
        except ValueError:
            errMsg = str.format(invalidValue, badVal=n)

        if not errMsg:
            if cOpt != "-c":
                errMsg = str.format(invalidOption, badVal=cOpt[1:])  # format the error message as we would expect it!
            else:
                try:
                    c = int(c)
                    if not (0 < c < n):
                        errMsg = invalidNorC
                except ValueError:
                    errMsg = str.format(invalidValue, badVal=c)

                if not errMsg:
                    if iOpt != "-i":
                        errMsg = str.format(invalidOption,
                                            badVal=iOpt[1:])  # format the error message as we would expect it!
                    else:
                        try:
                            i = int(i)
                            if not (0 < i <= 20):
                                errMsg = invalidI
                        except ValueError:
                            errMsg = str.format(invalidValue, badVal=i)
# </editor-fold>

output = ""
try:
    output = subp.check_output([filename, passedArgs], shell=True,
                               stderr=subp.STDOUT)  # run program with provided arguments and then give me output if present.
    # Process ran normally, exit 0, check the output with #checkOutput
    # checking if the # of thread messges is correct, should be = to # of n (passengers)

    for x in range(n + 1):
        cntThrdMsg = getOutput(str.format(passBoardStr, x), output) # count how many times a thread boards

        # checking for at MOST c * i "ride" messages

except subp.CalledProcessError as rproc:  # returned process
    # Process returned non-zero error code (might be intended)
    if not errMsg:  # if you errored, when you shouldn't've.
        exit(1)

    good = errMsg == rproc.output  # Lol
    if not good:  # if you gave the wrong error message.
        exit(1)
exit(0)

# Idea:
# there are n passenger threads (0-(n-1))
# so for loop check each thread to see that theyre all there for 0, 1, 2, 3, 4.
# Each Passenger Thread will run between 0 and i times, inclusive
# there must be an exit thread message for each of the Passenger Threads
