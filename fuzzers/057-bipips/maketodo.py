#!/usr/bin/env python3

import os, re


def maketodo(pipfile, dbfile):
    todos = set()
    with open(pipfile, "r") as f:
        for line in f:
            line = line.split()
            todos.add(line[0])
    with open(dbfile, "r") as f:
        for line in f:
            line = line.split()
            if line[0] in todos:
                todos.remove(line[0])
    for line in todos:
        print(line)


maketodo(
    "bipips_int_l.txt", "%s/%s/segbits_int_l.db" %
    (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")))
maketodo(
    "bipips_int_r.txt", "%s/%s/segbits_int_r.db" %
    (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE")))
