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
    return Roi(
        db=db,
        x1=x1,
        x2=x2,
        y1=y1,
        y2=y2)


# we know that all bits for CLB MUXes are in frames 30 and 31, so filter all other bits
def bitfilter_clb_mux(frame_idx, bit_idx):
    return frame_idx in [30, 31]
