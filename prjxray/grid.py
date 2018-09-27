from collections import namedtuple

GridLoc = namedtuple('GridLoc', 'grid_x grid_y')
GridInfo = namedtuple('GridInfo', 'segment sites tile_type')


class Grid(object):
    """ Object that represents grid for a given database.

  Provides methods to inspect grid by name or location.  Also provides mapping
  of segment offsets for particular grid locations and their tile types.
  """

    def __init__(self, tilegrid):
        self.tilegrid = tilegrid
        self.loc = {}
        self.tileinfo = {}

        for tile in self.tilegrid['tiles']:
            tileinfo = self.tilegrid['tiles'][tile]
            grid_loc = GridLoc(tileinfo['grid_x'], tileinfo['grid_y'])
            self.loc[grid_loc] = tile
            self.tileinfo[tile] = GridInfo(
                segment=tileinfo['segment'] if 'segment' in tileinfo else None,
                sites=tileinfo['sites'],
                tile_type=tileinfo['type'])

        x, y = zip(*self.loc.keys())
        self._dims = (min(x), max(x), min(y), max(y))

    def tile_locations(self):
        """ Return list of tile locations. """
        return self.loc.keys()

    def dims(self):
        """ Returns (x_min, x_max, y_min, y_max) for given Grid. """
        return self._dims

    def is_populated(self, grid_loc):
        return grid_loc in self.loc

    def loc_of_tilename(self, tilename):
        tileinfo = self.tilegrid['tiles'][tilename]
        return GridLoc(tileinfo['grid_x'], tileinfo['grid_y'])

    def tilename_at_loc(self, grid_loc):
        return self.loc[grid_loc]

    def gridinfo_at_loc(self, grid_loc):
        return self.tileinfo[self.loc[grid_loc]]

    def gridinfo_at_tilename(self, tilename):
        return self.tileinfo[tilename]
