import os
import re
from .roi import Roi
from .db import Database


def get_db_root():
    return "%s/%s" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"))


def roi_xy():
    x1 = int(os.getenv('XRAY_ROI_GRID_X1'))
    x2 = int(os.getenv('XRAY_ROI_GRID_X2'))
    y1 = int(os.getenv('XRAY_ROI_GRID_Y1'))
    y2 = int(os.getenv('XRAY_ROI_GRID_Y2'))

    return (x1, x2), (y1, y2)


def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for xrange)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(
        r'SLICE_X([0-9]*)Y([0-9]*):SLICE_X([0-9]*)Y([0-9]*)',
        os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))


def get_roi():
    (x1, x2), (y1, y2) = roi_xy()
    db = Database(get_db_root())
    return Roi(db=db, x1=x1, x2=x2, y1=y1, y2=y2)


def gen_sites_xy(site_types):
    for _tile_name, site_name, _site_type in get_roi().gen_sites(site_types):
        m = re.match(r'.*_X([0-9]*)Y([0-9]*)', site_name)
        x, y = int(m.group(1)), int(m.group(2))
        yield (site_name, (x, y))


def site_xy_minmax(site_types):
    '''Return (X1, X2), (Y1, Y2) from XY_ROI, exclusive end (for xrange)'''
    xmin = 9999
    xmax = -1
    ymin = 9999
    ymax = -1
    for _site_name, (x, y) in gen_sites_xy(site_types):
        xmin = min(xmin, x)
        xmax = max(xmax, x)
        ymin = min(ymin, y)
        ymax = max(ymax, y)
    return (xmin, xmax + 1), (ymin, ymax + 1)


# we know that all bits for CLB MUXes are in frames 30 and 31, so filter all other bits
def bitfilter_clb_mux(frame_idx, bit_idx):
    return frame_idx in [30, 31]


def db_root_arg(parser):
    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)
    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)


def parse_db_line(line):
    '''Return tag name, bit values (if any), mode (if any)'''
    parts = line.split()
    # Ex: CLBLL_L.SLICEL_X0.AMUX.A5Q
    assert len(parts), "Empty line"
    tag = parts[0]
    if tag == 'bit':
        raise ValueError("Wanted bits db but got mask db")
    assert re.match(r'[A-Z0-9_.]+',
                    tag), "Invalid tag name: %s, line: %s" % (tag, line)
    orig_bits = line.replace(tag + " ", "")
    # <0 candidates> etc
    # Ex: INT_L.BYP_BOUNCE5.BYP_ALT5 always
    if "<" in orig_bits or "always" == orig_bits:
        return tag, None, orig_bits

    bits = frozenset(parts[1:])
    # Ex: CLBLL_L.SLICEL_X0.AOUTMUX.A5Q !30_06 !30_08 !30_11 30_07
    for bit in bits:
        # 19_39
        # 100_319
        assert re.match(r'[!]*[0-9]+_[0-9]+', bit), "Invalid bit: %s" % bit
    return tag, bits, None
