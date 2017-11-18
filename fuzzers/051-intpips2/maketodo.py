#!/usr/bin/env python3

import os, re

def maketodo(pipfile, dbfile):
    todos = set()
    with open(pipfile, "r") as f:
        for line in f:
            todos.add(line.split()[0])
    with open(dbfile, "r") as f:
        for line in f:
            todos.remove(line.split()[0])
    for line in todos:
        if line.endswith(".VCC_WIRE"):
            continue
        if line.endswith(".GND_WIRE"):
            continue
        if re.match(r".*\.(L[HV]B?|G?CLK)(_L)?(_B)?[0-9]", line):
            continue
        if re.match(r"^INT_[LR]\.(CTRL|GFAN)(_L)?[0-9]", line):
            continue
        print(line)

maketodo("pips_int_l.txt", "%s/%s/segbits_int_l.db" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")))
maketodo("pips_int_r.txt", "%s/%s/segbits_int_r.db" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")))

