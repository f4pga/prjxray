import os
import shutil
import sys
import subprocess
import signal
from multiprocessing import Pool
from itertools import chain

# Can be used to redirect vivado tons of output
# stdout=DEVNULL in subprocess.check_call
#try:
#    from subprocess import DEVNULL
#except ImportError:
#    import os
#    DEVNULL = open(os.devnull, 'wb')


# Worker function called from threads
def start_vivado(argList):
    blockID, start, stop = argList
    print("Running instance :" + str(blockID))
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/job.tcl -tclargs " +
        str(blockID) + " " + str(start) + " " + str(stop),
        shell=True)


# Function called once to get the total numbers of pips to list
def get_nb_pips():
    print("Fetching total number of pips")
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/get_pipscount.tcl",
        shell=True)
    countfile = open("nb_pips.txt", "r")
    return int(countfile.readline())


def main(argv):
    nbBlocks = 64
    nbParBlock = 4

    pipscount = get_nb_pips()
    blocksize = int(pipscount / nbBlocks)
    intPipsCount = blocksize * nbBlocks

    # We handle the case of not integer multiple of pips
    lastRun = False
    modBlocks = pipscount % nbBlocks
    if modBlocks != 0:
        lastRun = True
        nbBlocks = nbBlocks + 1

    if not os.path.exists("wires"):
        os.mkdir("wires")

    print(
        "Pips Count: " + str(pipscount) + " - Number of blocks: " +
        str(nbBlocks) + " - Parallel blocks: " + str(nbParBlock) +
        " - Blocksize: " + str(blocksize) + " - Modulo Blocks: " +
        str(modBlocks))

    blockId = range(0, nbBlocks)
    startI = range(0, intPipsCount, blocksize)
    stopI = range(blocksize, intPipsCount + 1, blocksize)

    # In case we have a last incomplete block we add it as a last
    # element in the arguments list
    if lastRun == True:
        startI = chain(startI, [intPipsCount])
        stopI = chain(stopI, [pipscount])

    argList = zip(blockId, startI, stopI)

    with Pool(processes=nbParBlock) as pool:
        pool.map(start_vivado, argList)

    print("Generating final files")

    with open("uphill_wires.txt", "w") as wfd:
        for j in range(0, nbBlocks):
            f = "wires/uphill_wires_" + str(j) + ".txt"
            with open(f, "r") as fd:
                shutil.copyfileobj(fd, wfd)

    with open("downhill_wires.txt", "w") as wed:
        for j in range(0, nbBlocks):
            e = "wires/downhill_wires_" + str(j) + ".txt"
            with open(e, "r") as ed:
                shutil.copyfileobj(ed, wed)

    print("Work done !")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
