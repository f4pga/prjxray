"""Tool to take site pin output and generate tile wire lists."""

from __future__ import print_function
import json
import json5
import sys


def main():
    site_pins = json5.load(sys.stdin)

    wires = {
        'tile_type': site_pins['tile_type'],
        'wires': [],
    }

    tile_prefix = site_pins['tile_name'] + '/'
    for node in site_pins['nodes']:
        wires['wires'].extend(
            wire[len(tile_prefix):]
            for wire in node['wires']
            if wire.startswith(tile_prefix))

    json.dump(wires, sys.stdout, indent=2)
    sys.stdout.write('\n')


if __name__ == "__main__":
    main()
