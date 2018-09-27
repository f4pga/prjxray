""" Reduce tile types to prototypes that are always correct.

The dump-all generate.tcl dumps all instances of each tile type.  Some tiles
are missing wires.  reduce_tile_types.py generates the superset tile that
encompases all tiles of that type.  If it is not possible to generate a super
set tile, an error will be generated.

"""

import argparse
import prjxray.lib
import datetime
import os.path
import json
import pyjson5 as json5
import progressbar
import multiprocessing
import os
import functools
import re


def check_and_strip_prefix(name, prefix):
    assert name.startswith(prefix), repr((name, prefix))
    return name[len(prefix):]


def flatten_site_pins(tile, site, site_pins, site_pin_node_to_wires):
    def inner():
        for site_pin in site_pins:
            wires = tuple(site_pin_node_to_wires(tile, site_pin['node']))

            if len(wires) == 0:
                yield (
                    check_and_strip_prefix(site_pin['site_pin'], site + '/'),
                    None)
                continue

            assert len(wires) == 1, repr(wires)

            yield (
                check_and_strip_prefix(site_pin['site_pin'], site + '/'),
                wires[0])

    return dict(inner())


# All site names appear to follow the pattern <type>_X<abs coord>Y<abs coord>.
# Generally speaking, only the tile relatively coordinates are required to
# assemble arch defs, so we re-origin the coordinates to be relative to the tile
# (e.g. start at X0Y0) and discard the prefix from the name.
SITE_COORDINATE_PATTERN = re.compile('^(.+)_X([0-9]+)Y([0-9]+)$')


def find_origin_coordinate(sites):
    """ Find the coordinates of each site within the tile, and then subtract the
      smallest coordinate to re-origin them all to be relative to the tile.
  """

    if len(sites) == 0:
        return 0, 0

    def inner_():
        for site in sites:
            coordinate = SITE_COORDINATE_PATTERN.match(site['site'])
            assert coordinate is not None, site

            x_coord = int(coordinate.group(2))
            y_coord = int(coordinate.group(3))
            yield x_coord, y_coord

    x_coords, y_coords = zip(*inner_())
    min_x_coord = min(x_coords)
    min_y_coord = min(y_coords)

    return min_x_coord, min_y_coord


def get_sites(tile, site_pin_node_to_wires):
    min_x_coord, min_y_coord = find_origin_coordinate(tile['sites'])

    for site in tile['sites']:
        orig_site_name = site['site']
        coordinate = SITE_COORDINATE_PATTERN.match(orig_site_name)

        x_coord = int(coordinate.group(2))
        y_coord = int(coordinate.group(3))

        yield (
            {
                'name':
                'X{}Y{}'.format(x_coord - min_x_coord, y_coord - min_y_coord),
                'prefix':
                coordinate.group(1),
                'x_coord':
                x_coord - min_x_coord,
                'y_coord':
                y_coord - min_y_coord,
                'type':
                site['type'],
                'site_pins':
                dict(
                    flatten_site_pins(
                        tile['tile'], site['site'], site['site_pins'],
                        site_pin_node_to_wires)),
            })


def compare_sites_and_update(tile, sites, new_sites):
    for site_a, site_b in zip(sites, new_sites):
        assert site_a['type'] == site_b['type']
        assert site_a['site_pins'].keys() == site_b['site_pins'].keys()

        for site_pin in site_a['site_pins']:
            if site_a['site_pins'][site_pin] is not None and site_b[
                    'site_pins'][site_pin] is not None:
                assert site_a['site_pins'][site_pin] == site_b['site_pins'][
                    site_pin]
            elif site_a['site_pins'][site_pin] is None and site_b['site_pins'][
                    site_pin] is not None:
                site_a['site_pins'][site_pin] = site_b['site_pins'][site_pin]


def get_prototype_site(site):
    proto = {}
    proto['type'] = site['type']
    proto['site_pins'] = {}
    proto['site_pips'] = {}
    for site_pin in site['site_pins']:
        name = check_and_strip_prefix(site_pin['site_pin'], site['site'] + '/')

        proto['site_pins'][name] = {
            'direction': site_pin['direction'],
        }

    for site_pip in site['site_pips']:
        name = check_and_strip_prefix(site_pip['site_pip'], site['site'] + '/')

        proto['site_pips'][name] = {
            'to_pin': site_pip['to_pin'],
            'from_pin': site_pip['from_pin'],
        }

    return proto


def get_pips(tile, pips):
    proto_pips = {}

    for pip in pips:
        name = check_and_strip_prefix(pip['pip'], tile + '/')

        proto_pips[name] = {
            'src_wire':
            check_and_strip_prefix(pip['src_wire'], tile + '/')
            if pip['src_wire'] is not None else None,
            'dst_wire':
            check_and_strip_prefix(pip['dst_wire'], tile + '/')
            if pip['dst_wire'] is not None else None,
            'is_pseudo':
            pip['is_pseudo'],
            'is_directional':
            pip['is_directional'],
            'can_invert':
            pip['can_invert'],
        }

    return proto_pips


def compare_and_update_pips(pips, new_pips):
    # Pip names are always the same, but sometimes the src_wire or dst_wire
    # may be missing.

    assert pips.keys() == new_pips.keys(), repr((pips.keys(), new_pips.keys()))
    for name in pips:
        if pips[name]['src_wire'] is not None and new_pips[name][
                'src_wire'] is not None:
            assert pips[name]['src_wire'] == new_pips[name]['src_wire'], repr(
                (
                    pips[name]['src_wire'],
                    new_pips[name]['src_wire'],
                ))
        elif pips[name]['src_wire'] is None and new_pips[name][
                'src_wire'] is not None:
            pips[name]['src_wire'] = new_pips[name]['src_wire']

        if pips[name]['dst_wire'] is not None and new_pips[name][
                'dst_wire'] is not None:
            assert pips[name]['dst_wire'] == new_pips[name]['dst_wire'], repr(
                (
                    pips[name]['dst_wire'],
                    new_pips[name]['dst_wire'],
                ))
        elif pips[name]['dst_wire'] is None and new_pips[name][
                'dst_wire'] is not None:
            pips[name]['dst_wire'] = new_pips[name]['dst_wire']

        for k in ['is_pseudo', 'is_directional', 'can_invert']:
            assert pips[name][k] == new_pips[name][k], (
                k, pips[name][k], new_pips[name][k])


def check_wires(wires, sites, pips):
    """ Verify that the wires generates from nodes are a superset of wires in
      sites and pips """
    if sites is not None:
        for site in sites:
            for wire_to_site_pin in site['site_pins'].values():
                if wire_to_site_pin is not None:
                    assert wire_to_site_pin in wires, repr(
                        (wire_to_site_pin, wires))

    if pips is not None:
        for pip in pips.values():
            if pip['src_wire'] is not None:
                assert pip['src_wire'] in wires, repr((pip['src_wire'], wires))
            if pip['dst_wire'] is not None:
                assert pip['dst_wire'] in wires, repr((pip['dst_wire'], wires))


def read_json5(fname, nodes):
    node_lookup = prjxray.lib.NodeLookup()
    node_lookup.load_from_nodes(nodes)

    #print('{} Reading {} (in pid {})'.format(datetime.datetime.now(), fname, os.getpid()))
    with open(fname) as f:
        tile = json5.load(f)

    #print('{} Done reading {}'.format(datetime.datetime.now(), fname))
    def get_site_types():
        for site in tile['sites']:
            yield get_prototype_site(site)

    site_types = tuple(get_site_types())
    sites = tuple(get_sites(tile, node_lookup.site_pin_node_to_wires))
    pips = get_pips(tile['tile'], tile['pips'])

    def inner():
        for wire in tile['wires']:
            assert wire['wire'].startswith(tile['tile'] + '/')
            yield wire['wire'][len(tile['tile']) + 1:]

    wires = set(inner())
    wires_from_nodes = set(node_lookup.wires_for_tile(tile['tile']))
    assert len(wires_from_nodes - wires) == 0, repr((wires, wires_from_nodes))

    return fname, tile, site_types, sites, pips, wires


def reduce_tile(pool, site_types, tile_type, tile_instances, node_lookup):
    sites = None
    pips = None
    wires = set()

    with progressbar.ProgressBar(max_value=len(tile_instances)) as bar:
        chunksize = 20
        if len(tile_instances) < chunksize * 2:
            iter = map(
                lambda file: read_json5(file, node_lookup.nodes),
                tile_instances)
        else:
            print(
                '{} Using pool.imap_unordered'.format(datetime.datetime.now()))
            iter = pool.imap_unordered(
                functools.partial(read_json5, nodes=node_lookup.nodes),
                tile_instances,
                chunksize=chunksize,
            )

        for idx, (fname, tile, new_site_types, new_sites, new_pips,
                  new_wires) in enumerate(iter):
            bar.update(idx)

            assert tile['type'] == tile_type, repr((tile['tile'], tile_type))

            for site_type in new_site_types:
                if site_type['type'] in site_types:
                    prjxray.lib.compare_prototype_site(
                        site_type, site_types[site_type['type']])
                else:
                    site_types[site_type['type']] = site_type

            # Sites are expect to always be the same
            if sites is None:
                sites = new_sites
            else:
                compare_sites_and_update(tile['tile'], sites, new_sites)

            if pips is None:
                pips = new_pips
            else:
                compare_and_update_pips(pips, new_pips)

            wires |= new_wires

            bar.update(idx + 1)

    check_wires(wires, sites, pips)

    return {
        'tile_type': tile_type,
        'sites': sites,
        'pips': pips,
        'wires': tuple(wires),
    }


def main():
    parser = argparse.ArgumentParser(
        description=
        "Reduces raw database dump into prototype tiles, grid, and connections."
    )
    parser.add_argument('--root_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--ignore_cache', action='store_true')

    args = parser.parse_args()

    print('{} Reading root.csv'.format(datetime.datetime.now()))
    tiles, nodes = prjxray.lib.read_root_csv(args.root_dir)

    print('{} Loading node<->wire mapping'.format(datetime.datetime.now()))
    node_lookup = prjxray.lib.NodeLookup()
    node_lookup_file = os.path.join(args.output_dir, 'nodes.pickle')
    if os.path.exists(node_lookup_file) and not args.ignore_cache:
        node_lookup.load_from_file(node_lookup_file)
    else:
        node_lookup.load_from_root_csv(nodes)
        node_lookup.save_to_file(node_lookup_file)

    site_types = {}

    processes = min(multiprocessing.cpu_count(), 10)
    print('Running {} processes'.format(processes))
    pool = multiprocessing.Pool(processes=processes)

    for tile_type in sorted(tiles.keys()):
        #for tile_type in ['CLBLL_L', 'CLBLL_R', 'CLBLM_L', 'CLBLM_R', 'INT_L', 'INT_L']:
        tile_type_file = os.path.join(
            args.output_dir, 'tile_type_{}.json'.format(tile_type))
        site_types = {}
        if os.path.exists(tile_type_file):
            print(
                '{} Skip reduced tile for {}'.format(
                    datetime.datetime.now(), tile_type))
            continue
        print(
            '{} Generating reduced tile for {}'.format(
                datetime.datetime.now(), tile_type))
        reduced_tile = reduce_tile(
            pool, site_types, tile_type, tiles[tile_type], node_lookup)
        for site_type in site_types:
            with open(os.path.join(
                    args.output_dir, 'tile_type_{}_site_type_{}.json'.format(
                        tile_type, site_types[site_type]['type'])), 'w') as f:
                json.dump(site_types[site_type], f, indent=2)

        with open(tile_type_file, 'w') as f:
            json.dump(reduced_tile, f, indent=2)


if __name__ == '__main__':
    main()
