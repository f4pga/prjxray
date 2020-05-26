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
import shutil
import sys
import subprocess
from multiprocessing import Pool
from itertools import chain
import argparse

# Can be used to redirect vivado tons of output
# stdout=DEVNULL in subprocess.check_call


# Worker function called from threads
def start_tiles(argList):
    blockID, start, stop, total = argList
    print("Running instance :" + str(blockID) + " / " + str(total))
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/jobtiles.tcl -tclargs " +
        str(blockID) + " " + str(start) + " " + str(stop),
        shell=True)


def start_nodes(argList):
    blockID, start, stop, total = argList
    print("Running instance :" + str(blockID) + " / " + str(total))
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/jobnodes.tcl -tclargs " +
        str(blockID) + " " + str(start) + " " + str(stop),
        shell=True)


# Function called once to get the total numbers of tiles to list
def get_nb_tiles():
    print("Fetching total number of tiles")
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/get_tilescount.tcl",
        shell=True)
    countfile = open("nb_tiles.txt", "r")
    return int(countfile.readline())


def get_nb_nodes():
    print("Fetching total number of nodes")
    subprocess.check_call(
        "${XRAY_VIVADO} -mode batch -source $FUZDIR/get_nodescount.tcl",
        shell=True)
    countfile = open("nb_nodes.txt", "r")
    return int(countfile.readline())


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

    argList = zip(blockId, startI, stopI, totalBlock)

    with Pool(processes=nbParBlock) as pool:
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
        "--sizeTilesBlock",
        help="Define the number of tiles to process per instance",
        type=int,
        default=300)
    parser.add_argument(
        "-n",
        "--sizeNodesBlock",
        help="Define the number of nodes to process per instance",
        type=int,
        default=30000)
    args = parser.parse_args()

    nbParBlock = args.nbPar
    blockTilesSize = args.sizeTilesBlock
    blockNodesSize = args.sizeNodesBlock

    print(
        " nbPar: " + str(nbParBlock) + " blockTilesSize: " +
        str(blockTilesSize) + " blockNodesSize: " + str(blockNodesSize))

    tilescount = get_nb_tiles()
    nbTilesBlocks = int(tilescount / blockTilesSize)

    tilesFileCount = run_pool(
        tilescount, nbTilesBlocks, blockTilesSize, nbParBlock, start_tiles)

    nodescount = get_nb_nodes()
    nbNodesBlocks = int(nodescount / blockNodesSize)

    nodeFilesCount = run_pool(
        nodescount, nbNodesBlocks, blockNodesSize, nbParBlock, start_nodes)

    print("Generating final csv files")

    with open("root.csv", "w") as wfd:
        wfd.write("filetype,subtype,filename\n")
        for j in range(0, tilesFileCount):
            ftiles = "root_" + str(j) + ".csv"
            with open(ftiles, "r") as fd:
                shutil.copyfileobj(fd, wfd)
        for j in range(0, nodeFilesCount):
            fnodes = "root_node_" + str(j) + ".csv"
            with open(fnodes, "r") as fd:
                shutil.copyfileobj(fd, wfd)

    print("Work done !")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
