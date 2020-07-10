class Overlay(object):
    """ Object that represents an overlay.

    Can be used to iterate over tiles and sites not inside a partition region.

    """

    def __init__(self, db, region_dict):
        self.grid = db.grid()
        self.region_dict = region_dict

    def tile_in_roi(self, grid_loc):
        """ Returns true if grid_loc (GridLoc tuple) is within the overlay. """
        x = grid_loc.grid_x
        y = grid_loc.grid_y
        for _, bounds in self.region_dict.items():
            x1, x2, y1, y2 = bounds
            if x1 <= x and x <= x2 and y1 <= y and y <= y2:
                return False
        return True

    def gen_tiles(self, tile_types=None):
        ''' Yield tile names within overlay.

        tile_types: list of tile types to keep, or None for all
        '''

        for tile_name in self.grid.tiles():
            loc = self.grid.loc_of_tilename(tile_name)

            if not self.tile_in_roi(loc):
                continue

            gridinfo = self.grid.gridinfo_at_loc(loc)

            if tile_types is not None and gridinfo.tile_type not in tile_types:
                continue

            yield tile_name

    def gen_sites(self, site_types=None):
        ''' Yield (tile_name, site_name, site_type) within overlay.

        site_types: list of site types to keep, or None for all

        '''

        for tile_name in self.grid.tiles():
            loc = self.grid.loc_of_tilename(tile_name)

            if not self.tile_in_roi(loc):
                continue

            gridinfo = self.grid.gridinfo_at_loc(loc)

            for site_name, site_type in gridinfo.sites.items():
                if site_types is not None and site_type not in site_types:
                    continue

                yield (tile_name, site_name, site_type)
