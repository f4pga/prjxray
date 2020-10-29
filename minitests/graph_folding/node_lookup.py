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
import sqlite3


def create_tables(conn):
    c = conn.cursor()

    c.executescript(
        """
CREATE TABLE tile_type(
    pkey INTEGER PRIMARY KEY,
    name TEXT
    );

CREATE TABLE wire_in_tile(
    pkey            INTEGER PRIMARY KEY,
    tile_type_pkey  INTEGER,
    name            TEXT,
    FOREIGN KEY(tile_type_pkey) REFERENCES tile_type(pkey)
    );

CREATE TABLE tile(
    pkey            INTEGER PRIMARY KEY,
    tile_type_pkey  INTEGER,
    x               INTEGER,
    y               INTEGER,
    name            TEXT,
    FOREIGN KEY(tile_type_pkey) REFERENCES tile_type(pkey)
    );

CREATE TABLE node(
    pkey INTEGER PRIMARY KEY,
    tile_pkey           INTEGER,
    wire_in_tile_pkey   INTEGER,
    FOREIGN KEY(tile_pkey) REFERENCES tile(pkey),
    FOREIGN KEY(wire_in_tile_pkey) REFERENCES wire_in_tile(pkey)
    );

CREATE TABLE wire(
    pkey                INTEGER PRIMARY KEY,
    tile_pkey           INTEGER,
    wire_in_tile_pkey   INTEGER,
    node_pkey           INTEGER,
    FOREIGN KEY(tile_pkey) REFERENCES tile(pkey),
    FOREIGN KEY(wire_in_tile_pkey) REFERENCES wire_in_tile(pkey),
    FOREIGN KEY(node_pkey) REFERENCES node(pkey)
    );
    """)

    conn.commit()


class NodeLookup(object):
    def __init__(self, database):
        self.conn = sqlite3.connect(database)

    def build_database(self, db, progressbar=lambda x: x):
        create_tables(self.conn)

        grid = db.grid()

        c = self.conn.cursor()

        tile_type_pkeys = {}
        wire_in_tile_pkeys = {}
        for tile_type_name in db.get_tile_types():
            c.execute(
                "INSERT INTO tile_type(name) VALUES (?);", (tile_type_name, ))
            tile_type_pkey = c.lastrowid
            tile_type_pkeys[tile_type_name] = tile_type_pkey
            tile_type = db.get_tile_type(tile_type_name)
            tile_type
            for wire in tile_type.get_wires():
                c.execute(
                    "INSERT INTO wire_in_tile(name, tile_type_pkey) VALUES (?, ?);",
                    (wire, tile_type_pkey))
                wire_in_tile_pkeys[tile_type_name, wire] = c.lastrowid

        tile_pkeys = {}
        for tile_name in progressbar(grid.tiles()):
            x, y = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_tilename(tile_name)
            tile_type = gridinfo.tile_type
            c.execute(
                "INSERT INTO tile(name, tile_type_pkey, x, y) VALUES (?, ?, ?, ?);",
                (tile_name, tile_type_pkeys[tile_type], x, y))
            tile_pkeys[tile_name] = c.lastrowid

        node_model = db.node_model(progressbar)

        for node_tile, node_wire in progressbar(node_model.get_nodes()):
            tile_pkey = tile_pkeys[node_tile]
            gridinfo = grid.gridinfo_at_tilename(node_tile)
            wire_in_tile_pkey = wire_in_tile_pkeys[gridinfo.
                                                   tile_type, node_wire]

            c.execute(
                "INSERT INTO node(tile_pkey, wire_in_tile_pkey) VALUES (?, ?);",
                (
                    tile_pkey,
                    wire_in_tile_pkey,
                ))
            node_pkey = c.lastrowid

            for tile, wire in node_model.get_wires_for_node(node_tile,
                                                            node_wire):
                tile_pkey = tile_pkeys[tile]
                gridinfo = grid.gridinfo_at_tilename(tile)
                wire_in_tile_pkey = wire_in_tile_pkeys[gridinfo.
                                                       tile_type, wire]
                c.execute(
                    """
INSERT INTO wire(tile_pkey, wire_in_tile_pkey, node_pkey) VALUES (?, ?, ?);""",
                    (tile_pkey, wire_in_tile_pkey, node_pkey))

        self.conn.commit()

        c = self.conn.cursor()
        c.execute("CREATE INDEX tile_type_names ON tile_type(name);")
        c.execute(
            "CREATE INDEX wire_names ON wire_in_tile(tile_type_pkey, name);")
        c.execute("CREATE INDEX tile_names ON tile(name);")
        c.execute("CREATE INDEX tile_xy ON tile(x, y);")
        c.execute(
            "CREATE INDEX node_tile_wire ON node(tile_pkey, wire_in_tile_pkey);"
        )
        c.execute("CREATE INDEX wire_tile ON wire(tile_pkey);")
        c.execute("CREATE INDEX wire_wire ON wire(wire_in_tile_pkey);")
        c.execute("CREATE INDEX wire_node ON wire(node_pkey);")
        self.conn.commit()
