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
""" Database files available for a tile type. """
from collections import namedtuple
import json
from prjxray import lib
from prjxray.timing import fast_slow_tuple_to_corners, RcElement
from prjxray.util import OpenSafeFile

TileDbs = namedtuple(
    'TileDbs', 'segbits block_ram_segbits ppips mask tile_type')


class OutPinTiming(namedtuple('OutPinTiming', 'delays drive_resistance')):
    """ Timing for site output pins.

    Attributes
    ----------
    delays : dicts of PvtCorner to IntristicDelay
        Intristic delay of output pin.
    drive_resistance : float
        Resistance of drive output pin (milliOhms).

    """
    pass


class InPinTiming(namedtuple('InPinTiming', 'delays capacitance')):
    """ Timing for site input pins.

    Attributes
    ----------
    delays : dicts of PvtCorner to IntristicDelay
        Intristic delay of input pin.
    capacitance : float
        Capacitance of input pints (microFarads).

    """
    pass


class PipTiming(namedtuple('PipTiming',
                           'delays drive_resistance internal_capacitance')):
    """ Timing for pips.

    Attributes
    ----------
    delays : dicts of PvtCorner to IntristicDelay
        Intristic delay of pip.
    internal_capacitance : float
        Capacitance (microFarads) of pip (which is only seen if pip is used).
    drive_resistance : float
        Resistance of drive output pin (milliOhms).

    """
    pass


class Pip(namedtuple(
        'Pip',
    ('name', 'net_to', 'net_from', 'can_invert', 'is_directional', 'is_pseudo',
     'is_pass_transistor', 'timing', 'backward_timing'))):
    """ Pip information.

    Attributes
    ----------

    name : str
        Name of pip
    net_to : str
        Name of output tile wire when pip is unidirectional.
    net_from: str
        Name of input tile wire when pip is unidirectional.
    can_invert : bool
        Can this pip invert the signal.
    is_directional : bool
        True if this pip is unidirectional, False if this pip is
        unidirectional.
    is_pseudo : bool
        True if this pip is mark as a pseudo-pip.
    is_pass_transistor : bool
        True if this pip is non-isolating.
    timing : PipTiming
        Timing used when connecting net_from to net_to.  This is the only
        timing used when a pip is unidirectional.

        May be None if timing information is not present in the database.
    backward_timing : PipTiming
        Timing used when connecting net_to to net_from.  This is only used
        if the pip is bidirectional.

        May be None if timing information is not present in the database.

    """
    pass


class Site(namedtuple('Site', 'name prefix x y type site_pins')):
    """ Represents an instance of a site within a tile.

    Attributes
    ----------
    name : str
        Name of site within tile, instance specific.
    prefix : str
        Prefix of site naming in Xilinx parlance.
    type : str
        What type of slice this instance presents.
    site_pins : list of SitePin
        Instaces of site pins within this site and tile.  This is an tuple of
        SitePin tuples, and is specific to this instance of the site within
        the tile.

    """


class SitePin(namedtuple('SitePin', 'name wire timing')):
    """ Tuple representing a site pin within a tile.

    Sites are generic based on type, however sites are instanced
    within a tile 1 or more times.  The SitePin contains both site type generic
    information and tile type specific information.

    Attributes
    ----------
    name : str
        Site type specific name.  This name is expected to be the same for
        all sites of the same type.
    wire : str
        Wire name within the tile.  This name is site instance specific.
    timing : Either InPinTiming or OutPinTiming
        Timing of site pin. May be None if database lacks timing information.

    """


WireInfo = namedtuple('WireInfo', 'pips sites')

# Conversion factor from database to internal units.
RESISTANCE_FACTOR = 1e3
CAPACITANCE_FACTOR = 1e3


def get_pip_timing(pip_timing_json):
    """ Convert pip_timing_json JSON into PipTiming object.

    Returns
    -------
    If timing information is not present for this pip, returns None.
    If timing information is present, returns PipTiming.  Some fields may be
    None if the pip type lacks that field.

    """

    if pip_timing_json is None:
        return None

    delays = None

    if pip_timing_json.get('delay') is not None:
        delays = fast_slow_tuple_to_corners(pip_timing_json.get('delay'))

    in_cap = pip_timing_json.get('in_cap')
    if in_cap is not None:
        in_cap = float(in_cap) / CAPACITANCE_FACTOR
    else:
        in_cap = 0

    res = pip_timing_json.get('res')
    if res is not None:
        res = float(res) / RESISTANCE_FACTOR
    else:
        res = 0

    return PipTiming(
        delays=delays,
        drive_resistance=res,
        internal_capacitance=in_cap,
    )


def get_site_pin_timing(site_pin_info):
    """ Convert site_pin_info JSON into InPinTiming or OutPinTiming object.

    Returns
    -------
    If timing information is not present for this site pin, returns None.
    If this is an output pin, returns OutPinTiming.
    If this is an input pin, returns InPinTiming.

    """
    if isinstance(site_pin_info, str):
        return site_pin_info, None

    wire = site_pin_info['wire']

    if 'delay' not in site_pin_info:
        return None

    delays = fast_slow_tuple_to_corners(site_pin_info['delay'])

    if 'cap' in site_pin_info:
        assert 'res' not in site_pin_info
        return wire, InPinTiming(
            delays=delays,
            capacitance=float(site_pin_info['cap']) / CAPACITANCE_FACTOR,
        )
    else:
        assert 'res' in site_pin_info
        return wire, OutPinTiming(
            delays=delays,
            drive_resistance=float(site_pin_info['res']) / RESISTANCE_FACTOR,
        )


def get_wires(wires):
    """ Converts database input to dictionary of tile wires to wire timing.

    Returns dictionary of tile wire name to RcElement or None. """

    if isinstance(wires, list):
        # Handle old database gracefully.
        return {wire: None for wire in wires}

    output = {}

    for wire, rc_json in wires.items():
        if rc_json is None:
            output[wire] = RcElement(
                resistance=0,
                capacitance=0,
            )
        else:
            output[wire] = RcElement(
                resistance=float(rc_json['res']) / RESISTANCE_FACTOR,
                capacitance=float(rc_json['cap']) / CAPACITANCE_FACTOR,
            )

    return output


def is_pass_transistor(pip_json):
    """ Returns boolean if pip JSON indicates pip is a pass transistor.

    Always returns False if database lacks this information.
    """
    if 'is_pass_transistor' in pip_json:
        return bool(int(pip_json['is_pass_transistor']))
    else:
        return False


class Tile(object):
    """ Provides abstration of a tile in the database. """

    def __init__(self, tilename, tile_dbs):
        self.tilename = tilename
        self.tilename_upper = self.tilename.upper()
        self.tile_dbs = tile_dbs

        self.wires = None
        self.sites = None
        self.pips = None
        self.pips_by_name = {}

        def yield_sites(sites):
            for site in sites:
                site_pins = []
                for name, site_pin_info in site['site_pins'].items():
                    if site_pin_info is not None:
                        wire, timing = get_site_pin_timing(site_pin_info)
                        site_pins.append(
                            SitePin(
                                name=name,
                                wire=wire,
                                timing=timing,
                            ))
                    else:
                        site_pins.append(
                            SitePin(
                                name=name,
                                wire=None,
                                timing=None,
                            ))

                yield Site(
                    name=site['name'],
                    prefix=site['prefix'],
                    type=site['type'],
                    x=site['x_coord'],
                    y=site['y_coord'],
                    site_pins=site_pins,
                )

        def yield_pips(pips):
            for name, pip in pips.items():
                yield Pip(
                    name=name,
                    net_to=pip['dst_wire'],
                    net_from=pip['src_wire'],
                    can_invert=bool(int(pip['can_invert'])),
                    is_directional=bool(int(pip['is_directional'])),
                    is_pseudo=bool(int(pip['is_pseudo'])),
                    is_pass_transistor=is_pass_transistor(pip),
                    timing=get_pip_timing(pip.get('src_to_dst')),
                    backward_timing=get_pip_timing(pip.get('dst_to_src')),
                )

        with OpenSafeFile(self.tile_dbs.tile_type) as f:
            tile_type = json.load(f)
            assert self.tilename_upper == tile_type['tile_type']
            self.wires = get_wires(tile_type['wires'])
            self.sites = tuple(yield_sites(tile_type['sites']))
            self.pips = tuple(yield_pips(tile_type['pips']))

        self.wire_info = {}

    def get_wires(self):
        """Returns a set of wire names present in this tile."""
        return self.wires

    def get_sites(self):
        """ Returns tuple of Site namedtuple's present in this tile. """
        return self.sites

    def get_pips(self):
        """ Returns tuple of Pip namedtuple's representing the PIPs in this tile.
    """
        return self.pips

    def get_pip_by_name(self, name):
        if len(self.pips_by_name) == 0:
            for pip in self.pips:
                self.pips_by_name[pip.name] = pip

        return self.pips_by_name[name]

    def get_wire_info(self, target_wire, allow_pseudo=False):
        if len(self.wire_info) == 0:
            for wire in self.wires:
                pips = list()
                sites = list()

                for site in self.sites:
                    for site_pin in site.site_pins:
                        if site_pin.wire == wire:
                            sites.append((site.name, site_pin.name))

                for pip in self.pips:
                    pseudo_filter = (not pip.is_pseudo) or allow_pseudo
                    if (wire == pip.net_to
                            or wire == pip.net_from) and pseudo_filter:
                        pips.append(pip.name)

                assert wire not in self.wire_info
                self.wire_info[wire] = WireInfo(pips=pips, sites=sites)

        return self.wire_info[target_wire]

    def get_instance_sites(self, grid_info):
        """ get_sites returns abstract sites for all tiles of type.
            get_instance_sites converts site info from generic to specific
            based on a tile location.
            """

        site_names = set()

        for site in self.sites:
            site_name = '{}_X{}Y{}'.format(site.prefix, site.x, site.y)
            origin_x, origin_y = lib.find_origin_coordinate(
                site_name, grid_info.sites.keys())

            x = site.x + origin_x
            y = site.y + origin_y

            site_name = '{}_X{}Y{}'.format(site.prefix, x, y)

            if site_name not in grid_info.sites:
                type_count = 0
                for site_name_from_grid, site_type in grid_info.sites.items():
                    if site.type == site_type:
                        type_count += 1
                        site_name = site_name_from_grid

                assert type_count == 1, (site_name, type_count)

            site_names.add(site_name)
            assert site.type == grid_info.sites[site_name]

            yield Site(
                name=site_name,
                prefix=site.prefix,
                type=site.type,
                x=x,
                y=y,
                site_pins=site.site_pins,
            )

        assert site_names == set(grid_info.sites.keys())


def get_other_wire_from_pip(pip, wire):
    if wire == pip.net_to:
        return pip.net_from
    elif wire == pip.net_from:
        return pip.net_to
    else:
        assert False, (pip, wire)
