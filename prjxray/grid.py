from collections import namedtuple
import enum
from prjxray import segment_map


class BlockType(enum.Enum):
    # Frames describing CLB features, interconnect, clocks and IOs.
    CLB_IO_CLK = 'CLB_IO_CLK'

    # Frames describing block RAM initialization.
    BLOCK_RAM = 'BLOCK_RAM'


GridLoc = namedtuple('GridLoc', 'grid_x grid_y')
GridInfo = namedtuple('GridInfo', 'segment bits sites tile_type')
Bits = namedtuple('Bits', 'base_address frames offset words')
BitsInfo = namedtuple('BitsInfo', 'segment_type tile bits')


class Grid(object):
    """ Object that represents grid for a given database.

  Provides methods to inspect grid by name or location.  Also provides mapping
  of segment offsets for particular grid locations and their tile types.
  """

    def __init__(self, tilegrid):
        self.tilegrid = tilegrid
        self.loc = {}
        self.tileinfo = {}
        # Map of segment name to tiles in that segment
        self.segments = {}

        # Map of (base_address, segment type) -> segment name
        self.base_addresses = {}

        # Map of base_address -> (segment type, segment name)
        self.base_addresses = {}

        for tile in self.tilegrid:
            tileinfo = self.tilegrid[tile]
            grid_loc = GridLoc(tileinfo['grid_x'], tileinfo['grid_y'])
            assert grid_loc not in self.loc
            self.loc[grid_loc] = tile

            bits = {}

            if 'segment' in tileinfo:
                if tileinfo['segment'] not in self.segments:
                    self.segments[tileinfo['segment']] = []

                self.segments[tileinfo['segment']].append(tile)

            if 'bits' in tileinfo:
                for k in tileinfo['bits']:
                    segment_type = BlockType(k)
                    base_address = int(tileinfo['bits'][k]['baseaddr'], 0)
                    bits[segment_type] = Bits(
                        base_address=base_address,
                        frames=tileinfo['bits'][k]['frames'],
                        offset=tileinfo['bits'][k]['offset'],
                        words=tileinfo['bits'][k]['words'],
                    )

            self.tileinfo[tile] = GridInfo(
                segment=tileinfo['segment'] if 'segment' in tileinfo else None,
                bits=bits,
                sites=tileinfo['sites'],
                tile_type=tileinfo['type'],
            )

        x, y = zip(*self.loc.keys())
        self._dims = (min(x), max(x), min(y), max(y))

    def tiles(self):
        """ Return list of tiles. """
        return self.tileinfo.keys()

    def tile_locations(self):
        """ Return list of tile locations. """
        return self.loc.keys()

    def dims(self):
        """ Returns (x_min, x_max, y_min, y_max) for given Grid. """
        return self._dims

    def is_populated(self, grid_loc):
        return grid_loc in self.loc

    def loc_of_tilename(self, tilename):
        tileinfo = self.tilegrid[tilename]
        return GridLoc(tileinfo['grid_x'], tileinfo['grid_y'])

    def tilename_at_loc(self, grid_loc):
        return self.loc[grid_loc]

    def gridinfo_at_loc(self, grid_loc):
        return self.tileinfo[self.loc[grid_loc]]

    def gridinfo_at_tilename(self, tilename):
        return self.tileinfo[tilename]

    def iter_all_frames(self):
        for tile, tileinfo in self.tileinfo.items():
            for segment_type, bits in tileinfo.bits.items():
                yield BitsInfo(
                    segment_type=segment_type,
                    tile=tile,
                    bits=bits,
                )

    def get_segment_map(self):
        return segment_map.SegmentMap(self)
