import json


class Roi(object):
    def __init__(self, tilegrid_file, x1, x2, y1, y2):
        self.tilegrid_file = tilegrid_file
        self.tilegrid = None
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def tile_in_roi(self, tilej):
        x = int(tilej['grid_x'])
        y = int(tilej['grid_y'])
        return self.x1 <= x and x <= self.x2 and self.y1 <= y and y <= self.y2

    def read_tilegrid(self):
        if not self.tilegrid:
            with open(self.tilegrid_file) as f:
                self.tilegrid = json.load(f)

    def gen_tiles(self, tile_types=None):
        '''
        tile_types: list of tile types to keep, or None for all
        '''

        self.read_tilegrid()

        for tile_name, tilej in self.tilegrid.items():
            if self.tile_in_roi(tilej) and (tile_types is None
                                            or tilej['type'] in tile_types):
                yield (tile_name, tilej)

    def gen_sites(self, site_types=None):
        '''
        site_types: list of site types to keep, or None for all
        '''

        self.read_tilegrid()

        for tile_name, tilej in self.tilegrid.items():
            if not self.tile_in_roi(tilej):
                continue

            for site_name, site_type in tilej['sites'].items():
                if site_types is None or site_type in site_types:
                    yield (tile_name, site_name, site_type)
