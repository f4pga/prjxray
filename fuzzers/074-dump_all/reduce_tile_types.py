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
""" Reduce tile types to prototypes that are always correct.
The dump-all generate.tcl dumps all instances of each tile type.  Some tiles
are missing wires.  reduce_tile_types.py generates the superset tile that
encompases all tiles of that type.  If it is not possible to generate a super
set tile, an error will be generated.

"""

import argparse
import prjxray.lib
import prjxray.node_lookup
import datetime
import subprocess
import os.path
import pyjson5 as json5
import progressbar
import multiprocessing
import os
import functools
import json
from prjxray.xjson import extract_numbers


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

            pin_info = {
                'wire': wires[0],
                'speed_model_index': site_pin['speed_model_index'],
            }

            yield (
                check_and_strip_prefix(site_pin['site_pin'], site + '/'),
                pin_info)

    return dict(inner())


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
            'speed_model_index':
            pip['speed_model_index'],
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
                    assert wire_to_site_pin['wire'] in wires, repr(
                        (wire_to_site_pin, wires))

    if pips is not None:
        for pip in pips.values():
            if pip['src_wire'] is not None:
                assert pip['src_wire'] in wires, repr((pip['src_wire'], wires))
            if pip['dst_wire'] is not None:
                assert pip['dst_wire'] in wires, repr((pip['dst_wire'], wires))


def get_sites(tile, site_pin_node_to_wires):
    for site in tile['sites']:
        min_x_coord, min_y_coord = prjxray.lib.find_origin_coordinate(
            site['site'], (site['site'] for site in tile['sites']))

        orig_site_name = site['site']
        coordinate = prjxray.lib.get_site_coordinate_from_name(orig_site_name)

        x_coord = coordinate.x_coord - min_x_coord
        y_coord = coordinate.y_coord - min_y_coord

        yield (
            {
                'name':
                'X{}Y{}'.format(x_coord, y_coord),
                'prefix':
                coordinate.prefix,
                'x_coord':
                x_coord,
                'y_coord':
                y_coord,
                'type':
                site['type'],
                'site_pins':
                dict(
                    flatten_site_pins(
                        tile['tile'], site['site'], site['site_pins'],
                        site_pin_node_to_wires)),
            })


def read_json5(fname, database_file):
    node_lookup = prjxray.node_lookup.NodeLookup(database_file)

    with open(fname) as f:
        tile = json5.load(f)

    def get_site_types():
        for site in tile['sites']:
            yield get_prototype_site(site)

    site_types = tuple(get_site_types())
    sites = tuple(get_sites(tile, node_lookup.site_pin_node_to_wires))
    pips = get_pips(tile['tile'], tile['pips'])

    def inner():
        for wire in tile['wires']:
            assert wire['wire'].startswith(tile['tile'] + '/')

            wire_speed_model_index = wire['speed_model_index']

            yield wire['wire'][len(tile['tile']) + 1:], wire_speed_model_index

    wires = {k: v for (k, v) in inner()}
    wires_from_nodes = set(node_lookup.wires_for_tile(tile['tile']))
    assert len(wires_from_nodes - wires.keys()) == 0, repr(
        (wires, wires_from_nodes))

    return fname, tile, site_types, sites, pips, wires


def compare_and_update_wires(wires, new_wires):
    for wire in new_wires:
        if wire not in wires:
            wires[wire] = new_wires
        else:
            assert wires[wire] == new_wires[wire]


def get_speed_model_indices(reduced_tile):
    """ Extracts the speed model indices for the data structure """

    speed_model_indices = set()

    for site in reduced_tile['sites']:
        for site_pin in site['site_pins'].keys():
            if site['site_pins'][site_pin] is None:
                continue

            speed_model_indices.add(
                'site_pin,{}'.format(
                    site['site_pins'][site_pin]['speed_model_index']))

    for pip in reduced_tile['pips'].keys():
        speed_model_indices.add(
            'pip,{}'.format(reduced_tile['pips'][pip]['speed_model_index']))

    for wire in reduced_tile['wires'].keys():
        speed_model_indices.add('wire,{}'.format(reduced_tile['wires'][wire]))

    return speed_model_indices


def annotate_pips_speed_model(pips, speed_data):
    """ Updates the pips with correct timing data """

    for pip_name, pip_data in pips.items():
        speed_model_index = pip_data['speed_model_index']

        pip_speed_data = speed_data[speed_model_index]
        assert pip_speed_data['resource_name'] == 'pip', (
            pip_speed_data['resource_name'], speed_model_index)

        pips[pip_name]['is_pass_transistor'] = pip_speed_data[
            'is_pass_transistor']
        pips[pip_name]['src_to_dst'] = {
            'delay': pip_speed_data.get('forward_delay', None),
            'in_cap': pip_speed_data.get('forward_in_cap', None),
            'res': pip_speed_data.get('forward_res', None),
        }
        pips[pip_name]['dst_to_src'] = {
            'delay': pip_speed_data.get('reverse_delay', None),
            'in_cap': pip_speed_data.get('reverse_in_cap', None),
            'res': pip_speed_data.get('reverse_res', None),
        }

        del pips[pip_name]['speed_model_index']


def annotate_site_pins_speed_model(site_pins, speed_data):
    """ Updates the site_pins with correct timing data """

    for site_pin_name, pin_data in site_pins.items():
        if pin_data is None:
            continue

        speed_model_index = pin_data['speed_model_index']

        pin_speed_data = speed_data[speed_model_index]
        assert pin_speed_data['resource_name'] == 'site_pin', (
            pin_speed_data['resource_name'], speed_model_index)

        site_pins[site_pin_name]['delay'] = pin_speed_data['delay']

        cap = pin_speed_data['cap']
        res = pin_speed_data['res']
        if cap != 'null':
            site_pins[site_pin_name]['cap'] = cap
        if res != 'null':
            site_pins[site_pin_name]['res'] = res

        del site_pins[site_pin_name]['speed_model_index']


def annotate_wires_speed_model(wires, speed_data):
    """ Updates the wires with correct timing data """

    for wire_name, wire_data in wires.items():
        speed_model_index = wire_data

        wire_speed_data = speed_data[speed_model_index]
        assert wire_speed_data['resource_name'] == 'wire', (
            wire_speed_data['resource_name'], speed_model_index)

        cap = wire_speed_data['cap']
        res = wire_speed_data['res']
        if cap != '0.000' or res != '0.000':
            wires[wire_name] = {
                'cap': cap,
                'res': res,
            }
        else:
            wires[wire_name] = None


def annotate_speed_model(tile_type, reduced_tile, root_dir):
    """ Updates the reduced tile with the correct speed information """

    speed_model_indices = get_speed_model_indices(reduced_tile)

    tmp_indices_file = os.path.join(
        root_dir, '{}_speed_index.tmp'.format(tile_type))

    with open(tmp_indices_file, "w") as f:
        for index in speed_model_indices:
            print(index, file=f)

    # Get vivado path
    vivado = os.getenv('XRAY_VIVADO')
    assert vivado is not None

    subprocess.check_call(
        "{} -mode batch -source get_speed_model.tcl -tclargs {}".format(
            vivado, tmp_indices_file),
        shell=True,
        stdout=subprocess.DEVNULL)

    with open(tmp_indices_file, "r") as f:
        speed_model_data = json5.load(f)

    for site in reduced_tile['sites']:
        annotate_site_pins_speed_model(site['site_pins'], speed_model_data)

    annotate_pips_speed_model(reduced_tile['pips'], speed_model_data)
    annotate_wires_speed_model(reduced_tile['wires'], speed_model_data)


def reduce_tile(pool, site_types, tile_type, tile_instances, database_file):
    sites = None
    pips = None
    wires = None

    with progressbar.ProgressBar(max_value=len(tile_instances)) as bar:
        chunksize = 1
        if len(tile_instances) < chunksize * 2:
            iter = map(
                lambda file: read_json5(file, database_file), tile_instances)
        else:
            print(
                '{} Using pool.imap_unordered'.format(datetime.datetime.now()))
            iter = pool.imap_unordered(
                functools.partial(read_json5, database_file=database_file),
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

            if wires is None:
                wires = new_wires
            else:
                compare_and_update_wires(wires, new_wires)

            bar.update(idx + 1)

    check_wires(wires, sites, pips)

    return {
        'tile_type': tile_type,
        'sites': sites,
        'pips': pips,
        'wires': wires,
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
    database_file = os.path.join(args.output_dir, 'nodes.db')
    if os.path.exists(database_file) and not args.ignore_cache:
        node_lookup = prjxray.node_lookup.NodeLookup(database_file)
    else:
        node_lookup = prjxray.node_lookup.NodeLookup(database_file)
        node_lookup.build_database(nodes=nodes, tiles=tiles)

    site_types = {}

    processes = multiprocessing.cpu_count()
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
            pool, site_types, tile_type, tiles[tile_type], database_file)

        annotate_speed_model(tile_type, reduced_tile, args.root_dir)

        for site_type in site_types:
            with open(os.path.join(
                    args.output_dir, 'tile_type_{}_site_type_{}.json'.format(
                        tile_type, site_types[site_type]['type'])), 'w') as f:
                json.dump(site_types[site_type], f, indent=2, sort_keys=True)

        reduced_tile['sites'] = sorted(
            reduced_tile['sites'],
            key=lambda site: extract_numbers(
                '{}_{}'.format(site['name'], site['prefix'])))

        with open(tile_type_file, 'w') as f:
            json.dump(reduced_tile, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
