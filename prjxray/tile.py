from collections import namedtuple
import json
from prjxray import lib
""" Database files available for a tile """
TileDbs = namedtuple('TileDbs', 'segbits mask tile_type')

Pip = namedtuple('Pip', 'name net_to net_from can_invert is_directional is_pseudo')

""" Site - Represents an instance of a site within a tile.

name - Name of site within tile, instance specific.
prefix - Prefix of site naming in Xilinx parlance.
type - What type of slice this instance presents.
pins - Instaces of site pins within this site and tile.  This is an tuple of
       SitePin tuples, and is specific to this instance of the site within
       the tile.

"""
Site = namedtuple('Site', 'name prefix x y type site_pins')

""" SitePin - Tuple representing a site pin within a tile.

Sites are generic based on type, however sites are instanced
within a tile 1 or more times.  The SitePin contains both site type generic
information and tile type specific information.

name - Site type specific name.  This name is expected to be the same for all
       sites of the same type.
wire - Wire name within the tile.  This name is site instance specific.

"""
SitePin = namedtuple('SitePin', 'name wire')

WireInfo = namedtuple('WireInfo', 'pips sites')


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
                yield Site(
                    name=site['name'],
                    prefix=site['prefix'],
                    type=site['type'],
                    x=site['x_coord'],
                    y=site['y_coord'],
                    site_pins=tuple(
                        SitePin(
                            name=name,
                            wire=wire,
                        ) for name, wire in site['site_pins'].items()))

        def yield_pips(pips):
            for name, pip in pips.items():
                yield Pip(
                        name = name,
                    net_to=pip['dst_wire'],
                    net_from=pip['src_wire'],
                    can_invert=bool(int(pip['can_invert'])),
                    is_directional=bool(int(pip['is_directional'])),
                    is_pseudo=bool(int(pip['is_pseudo'])),
                )

        with open(self.tile_dbs.tile_type) as f:
            tile_type = json.load(f)
            assert self.tilename_upper == tile_type['tile_type']
            self.wires = tile_type['wires']
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
                    if (wire == pip.net_to or wire == pip.net_from) and pseudo_filter:
                        pips.append(pip.name)

                assert wire not in self.wire_info
                self.wire_info[wire] = WireInfo(pips=pips, sites=sites)

        return self.wire_info[target_wire]

    def get_instance_sites(self, grid_info):
        """ get_sites returns abstract sites for all tiles of type.
            get_instance_sites converts site info from generic to specific
            based on a tile location.
            """
        origin_x, origin_y = lib.find_origin_coordinate(grid_info.sites.keys())

        site_names = set()

        for site in self.sites:
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
