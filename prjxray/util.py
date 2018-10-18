import os
import re
import os
import json

DB_PATH = "%s/%s" % (
    os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"))


def roi_xy():
    x1 = int(os.getenv('XRAY_ROI_GRID_X1'))
    x2 = int(os.getenv('XRAY_ROI_GRID_X2'))
    y1 = int(os.getenv('XRAY_ROI_GRID_Y1'))
    y2 = int(os.getenv('XRAY_ROI_GRID_Y2'))

    return (x1, x2), (y1, y2)


(ROI_X1, ROI_X2), (ROI_Y1, ROI_Y2) = roi_xy()


def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for xrange)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(
        r'SLICE_X([0-9]*)Y([0-9]*):SLICE_X([0-9]*)Y([0-9]*)',
        os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))


def tile_in_roi(tilej):
    x = int(tilej['grid_x'])
    y = int(tilej['grid_y'])
    return ROI_X1 <= x <= ROI_X2 and ROI_Y1 <= y <= ROI_Y2


def load_tilegrid():
    return json.load(open('%s/tilegrid.json' % DB_PATH))


def gen_tiles(tile_types=None, tilegrid=None):
    '''
    tile_types: list of tile types to keep, or None for all
    tilegrid: cache the tilegrid database
    '''
    tilegrid = tilegrid or load_tilegrid()

    for tile_name, tilej in tilegrid.items():
        if tile_in_roi(tilej) and (tile_types is None
                                   or tilej['type'] in tile_types):
            yield (tile_name, tilej)


def gen_sites(site_types=None, tilegrid=None):
    '''
    site_types: list of site types to keep, or None for all
    tilegrid: cache the tilegrid database
    '''
    tilegrid = tilegrid or load_tilegrid()

    for tile_name, tilej in tilegrid.items():
        if not tile_in_roi(tilej):
            continue
        for site_name, site_type in tilej['sites'].items():
            if site_types is None or site_type in site_types:
                yield (tile_name, site_name, site_type)


#print(list(gen_tiles(['CLBLL_L', 'CLBLL_R', 'CLBLM_L', 'CLBLM_R'])))
#print(list(gen_sites(['SLICEL', 'SLICEM'])))
#print(list(gen_sites(['SLICEM'])))
