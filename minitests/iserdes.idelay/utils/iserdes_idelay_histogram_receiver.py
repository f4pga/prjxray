#!/usr/bin/env python3

"""
This script
"""

import serial

# =============================================================================


def main():
    
    # Open serial port
    port = serial.Serial("/dev/ttyUSB3", baudrate=115200)

    # Get first line and discard it. It may be broken
    port.readline()

    # Read and process lines
    while True:

        line = port.readline()
        line = line.decode("ASCII").strip()

        data = [int(x, base=16) for x in line.split("_")]
        print(" ".join("%4d" % x for x in data))

# =============================================================================


if __name__ == "__main__":
    main()

