#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import os
import shutil
import sys
import subprocess
import signal
from multiprocessing import Pool, Lock
from itertools import chain
import argparse

# Can be used to redirect vivado tons of output
# stdout=DEVNULL in subprocess.check_call


# Worker function called from threads.
# Once the worker completes the job, the temporary files
# get merged with the final outputs in a thread-safe way
# and deleted to save disk usage.
# To do so, a global Lock is provided at the Pool initialization.
def start_pips(argList):
    blockID, start, stop, total = argList
    print("Running instance :" + str(blockID) + " / " + str(total))
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/job.tcl -tclargs " +
        str(blockID) + " " + str(start) + " " + str(stop),
        shell=True)

    uphill_wires = "wires/uphill_wires_{}.txt".format(blockID)
    downhill_wires = "wires/downhill_wires_{}.txt".format(blockID)

    # Locking to write on final file and remove the temporary one
    Lock.acquire()
    with open("uphill_wires.txt", "a") as wfd:
        f = uphill_wires
        with open(f, "r") as fd:
            shutil.copyfileobj(fd, wfd)

    with open("downhill_wires.txt", "a") as wfd:
        f = downhill_wires
        with open(f, "r") as fd:
            shutil.copyfileobj(fd, wfd)
    Lock.release()

    os.remove(uphill_wires)
    os.remove(downhill_wires)


# Function called once to get the total numbers of pips to list
def get_nb_pips():
    print("Fetching total number of pips")
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/get_pipscount.tcl",
        shell=True)
    countfile = open("nb_pips.txt", "r")
    return int(countfile.readline())


def pool_init(lock):
    global Lock
    Lock = lock


def run_pool(itemcount, nbBlocks, blocksize, nbParBlock, workFunc):
    # We handle the case of not integer multiple of pips
    intitemcount = blocksize * nbBlocks
    lastRun = False
    modBlocks = itemcount - intitemcount
    if modBlocks != 0:
        lastRun = True
        nbBlocks = nbBlocks + 1

    print(
        "Items Count: " + str(itemcount) + " - Number of blocks: " +
        str(nbBlocks) + " - Parallel blocks: " + str(nbParBlock) +
        " - Blocksize: " + str(blocksize) + " - Modulo Blocks: " +
        str(modBlocks))

    blockId = range(0, nbBlocks)
    startI = range(0, intitemcount, blocksize)
    stopI = range(blocksize, intitemcount + 1, blocksize)
    totalBlock = [nbBlocks for _ in range(nbBlocks)]

    # In case we have a last incomplete block we add it as a last
    # element in the arguments list
    if lastRun == True:
        startI = chain(startI, [intitemcount])
        stopI = chain(stopI, [itemcount])

    mpLock = Lock()

    argList = zip(blockId, startI, stopI, totalBlock)

    with Pool(processes=nbParBlock, initializer=pool_init,
              initargs=(mpLock, )) as pool:
        pool.map(workFunc, argList)

    return nbBlocks


# ==========================================================================
# ===== FPGA Logic Items data ==============================================
# For Artix 7 50T:
#   - Total pips: 22002368
#   - Total tiles: 18055
#   - Total nodes: 1953452
# For Kintex 7 70T:
#   - Total pips: 29424910
#   - Total tiles: 24453
#   - Total nodes: 2663055
# For Zynq 7 z010:
#   - Total pips: 12462138
#   - Total tiles: 13440
#   - Total nodes: 1122477
# =========================================================================
# Dividing by about 64 over 4 core is not optimized but a default to run
# on most computer
# =========================================================================


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--nbPar",
        help="Number of parallel instances of Vivado",
        type=int,
        default=4)
    parser.add_argument(
        "-t",
        "--sizePipsBlock",
        help="Define the number of pips to process per instance",
        type=int,
        default=340000)
    args = parser.parse_args()

    nbParBlock = args.nbPar
    blockPipsSize = args.sizePipsBlock

    pipscount = get_nb_pips()
    nbPipsBlock = int(pipscount / blockPipsSize)

    if not os.path.exists("wires"):
        os.mkdir("wires")

    print(
        " nbPar: " + str(nbParBlock) + " blockPipsSize: " + str(blockPipsSize))

    pipsFileCount = run_pool(
        pipscount, nbPipsBlock, blockPipsSize, nbParBlock, start_pips)

    print("Work done !")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
