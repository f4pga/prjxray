from collections import namedtuple
import json
""" Database files available for a tile """
TileDbs = namedtuple('TileDbs', 'segbits mask tile_type')

Pip = namedtuple('Pip', 'net_to net_from can_invert is_directional is_pseudo')
""" Site - Represents an instance of a site within a tile.

name - Name of site within tile, instance specific.
prefix - Prefix of site naming in Xilinx parlance.
type - What type of slice this instance presents.
pins - Instaces of site pins within this site and tile.  This is an tuple of
       SitePin tuples, and is specific to this instance of the site within
       the tile.

"""
Site = namedtuple('Site', 'name x y type site_pins')
""" SitePin - Tuple representing a site pin within a tile.

Sites are generic based on type, however sites are instanced
within a tile 1 or more times.  The SitePin contains both site type generic
information and tile type specific information.

name - Site type specific name.  This name is expected to be the same for all
       sites of the same type.
direction - Direction of this site pin.  This direction is expected to be the
       same for all sites of the same type.
wire - Wire name within the tile.  This name is site instance specific.

"""
SitePin = namedtuple('SitePin', 'name wire direction')


class Tile(object):
    """ Provides abstration of a tile in the database. """

    def __init__(self, tilename, tile_dbs):
        self.tilename = tilename
        self.tilename_upper = self.tilename.upper()
        self.tile_dbs = tile_dbs

        self.wires = None
        self.sites = None
        self.pips = None

        def yield_sites(sites):
            for site in sites:
                yield Site(
                    name=None,
                    type=site['type'],
                    x=None,
                    y=None,
                    site_pins=site['site_pins'],
                )

        def yield_pips(pips):
            for pip in pips:
                yield Pip(
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
