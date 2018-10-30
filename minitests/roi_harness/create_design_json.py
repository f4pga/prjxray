import json
import csv
import argparse
import sys
from prjxray.db import Database
from prjxray.roi import Roi
from prjxray.util import get_db_root


def set_port_wires(ports, name, pin, wires_outside_roi):
    for port in ports:
        if name == port['name']:
            port['wires_outside_roi'] = wires_outside_roi
            assert port['pin'] == pin
            return

    assert False, name


def main():
    parser = argparse.ArgumentParser(
        description=
        "Creates design.json from output of ROI generation tcl script.")
    parser.add_argument('--design_txt', required=True)
    parser.add_argument('--design_info_txt', required=True)
    parser.add_argument('--pad_wires', required=True)

    args = parser.parse_args()

    j = {}
    j['ports'] = []
    j['info'] = {}
    with open(args.design_txt) as f:
        for d in csv.DictReader(f, delimiter=' '):
            j['ports'].append(d)

    with open(args.design_info_txt) as f:
        for l in f:
            name, value = l.strip().split(' = ')

            j['info'][name] = int(value)

    db = Database(get_db_root())
    grid = db.grid()

    roi = Roi(
        db=db,
        x1=j['info']['GRID_X_MIN'],
        y1=j['info']['GRID_Y_MIN'],
        x2=j['info']['GRID_X_MAX'],
        y2=j['info']['GRID_Y_MAX'],
    )

    with open(args.pad_wires) as f:
        for l in f:
            parts = l.strip().split(' ')
            name = parts[0]
            pin = parts[1]
            wires = parts[2:]

            wires_outside_roi = []

            for wire in wires:
                tile = wire.split('/')[0]

                loc = grid.loc_of_tilename(tile)

                if not roi.tile_in_roi(loc):
                    wires_outside_roi.append(wire)

            set_port_wires(j['ports'], name, pin, wires_outside_roi)

    json.dump(j, sys.stdout, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
