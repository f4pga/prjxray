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
import fcntl
import math
import os
import random
import re
import signal
import yaml
from .roi import Roi


def timeout_handler(signum, frame):
    raise Exception("ERROR TIMEOUT: could not lock file")


class OpenSafeFile:
    """
    Opens a file in a thread-safe mode, allowing for safe read and writes
    to a file that can potentially be modified by multiple processes at
    the same time.
    """

    def __init__(self, name, mode="r", timeout=10):
        self.name = name
        self.mode = mode
        self.timeout = timeout

        self.fd = None

    def __enter__(self):
        self.fd = open(self.name, self.mode)
        self.lock_file()
        return self.fd

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock_file()
        self.fd.close()

    def lock_file(self):
        assert self.fd is not None
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX)
            signal.alarm(0)
        except Exception as e:
            print(f"{e}: {self.name}")
            exit(1)

    def unlock_file(self):
        assert self.fd is not None
        fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)


def get_db_root():
    # Used during tilegrid db bootstrap
    ret = os.getenv("XRAY_DATABASE_ROOT", None)
    if ret:
        return ret

    return "%s/%s" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"))


def get_part():
    ret = os.getenv("XRAY_PART", None)

    return ret


def get_fabric():
    ret = os.getenv("XRAY_FABRIC", None)

    return ret


def get_part_information(db_root, part):
    filename = os.path.join(db_root, "mapping", "parts.yaml")
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)
    with open(filename, 'r') as stream:
        part_mapping = yaml.load(stream, Loader=yaml.FullLoader)
    part = part_mapping.get(part, None)
    assert part, "Part {} not found in {}".format(part, part_mapping)
    return part


def set_part_information(db_root, information):
    filename = os.path.join(db_root, "mapping", "parts.yaml")
    with OpenSafeFile(filename, 'w+') as stream:
        yaml.dump(information, stream)
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)


def get_part_resources(file_path, part):
    filename = os.path.join(file_path, "resources.yaml")
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)
    with open(filename, 'r') as stream:
        res_mapping = yaml.load(stream, Loader=yaml.FullLoader)
    res = res_mapping.get(part, None)
    assert res, "Part {} not found in {}".format(part, part_mapping)
    return res


def set_part_resources(file_path, information):
    filename = os.path.join(file_path, "resources.yaml")
    with OpenSafeFile(filename, 'w+') as stream:
        yaml.dump(information, stream)
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)


def get_fabric_for_part(db_root, part):
    filename = os.path.join(db_root, "mapping", "devices.yaml")
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)
    part = get_part_information(db_root, part)
    with OpenSafeFile(filename, 'r') as stream:
        device_mapping = yaml.load(stream, Loader=yaml.FullLoader)
    device = device_mapping.get(part['device'], None)
    assert device, "Device {} not found in {}".format(
        part['device'], device_mapping)
    return device['fabric']


def get_devices(db_root):
    filename = os.path.join(db_root, "mapping", "devices.yaml")
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)
    with open(filename, 'r') as stream:
        device_mapping = yaml.load(stream, Loader=yaml.FullLoader)
    return device_mapping


def get_parts(db_root):
    filename = os.path.join(db_root, "mapping", "parts.yaml")
    assert os.path.isfile(filename), \
        "Mapping file {} does not exist".format(filename)
    with open(filename, 'r') as stream:
        part_mapping = yaml.load(stream, Loader=yaml.FullLoader)
    return part_mapping


def roi_xy():
    x1 = int(os.getenv('XRAY_ROI_GRID_X1', 0))
    x2 = int(os.getenv('XRAY_ROI_GRID_X2', 58))
    y1 = int(os.getenv('XRAY_ROI_GRID_Y1', 0))
    y2 = int(os.getenv('XRAY_ROI_GRID_Y2', 52))

    return (x1, x2), (y1, y2)


def create_xy_fun(prefix):
    """ Create function that extracts X and Y coordinate from a prefixed string

    >>> fun = create_xy_fun(prefix='')
    >>> fun('X5Y23')
    (5, 23)
    >>> fun('X0Y0')
    (0, 0)
    >>> fun('X50Y100')
    (50, 100)

    >>> fun = create_xy_fun(prefix='SITE_')
    >>> fun('SITE_X5Y23')
    (5, 23)
    >>> fun('SITE_X0Y0')
    (0, 0)
    >>> fun('SITE_X50Y100')
    (50, 100)

    """
    compiled_re = re.compile(
        '^{prefix}X([0-9]+)Y([0-9]+)$'.format(prefix=prefix))

    def get_xy(s):
        m = compiled_re.match(s)
        assert m, (prefix, s)

        x = int(m.group(1))
        y = int(m.group(2))

        return x, y

    return get_xy


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
    from .db import Database
    (x1, x2), (y1, y2) = roi_xy()
    db = Database(get_db_root(), get_part())
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


def part_arg(parser):
    part = os.getenv("XRAY_PART")
    part_kwargs = {}
    if part is None:
        part_kwargs['required'] = True
    else:
        part_kwargs['required'] = False
        part_kwargs['default'] = part
    parser.add_argument(
        '--part',
        help="Part name. When not given defaults to XRAY_PART env. var.",
        **part_kwargs)


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
    if re.match(r'^origin:', orig_bits):
        origin = parts[1][7:]
        bits = frozenset(parts[2:])
        orig_bits = line.replace(tag + " " + origin + " ", "")
    else:
        origin = None
        bits = frozenset(parts[1:])
    # <0 candidates> etc
    # Ex: INT_L.BYP_BOUNCE5.BYP_ALT5 always
    if "<" in orig_bits or "always" == orig_bits:
        return tag, None, orig_bits, origin

    # Ex: CLBLL_L.SLICEL_X0.AOUTMUX.A5Q !30_06 !30_08 !30_11 30_07
    for bit in bits:
        # 19_39
        # 100_319
        assert re.match(r'[!]*[0-9]+_[0-9]+', bit), "Invalid bit: %s" % bit
    return tag, bits, None, origin


def parse_db_lines(fn):
    with OpenSafeFile(fn, "r") as f:
        for line in f:
            yield line, parse_db_line(line)


def write_db_lines(fn, entries, track_origin=False):
    new_lines = []
    for tag, (bits, origin) in entries.items():
        if track_origin:
            assert origin is not None
            new_line = " ".join([tag, "origin:" + origin] + sorted(bits))
        else:
            new_line = " ".join([tag] + sorted(bits))
        new_lines.append(new_line)

    with OpenSafeFile(fn, "w") as f:
        for line in sorted(new_lines):
            print(line, file=f)


def parse_tagbit(x):
    # !30_07
    if x[0] == '!':
        isset = False
        numstr = x[1:]
    else:
        isset = True
        numstr = x
    frame, word = numstr.split("_")
    # second part forms a tuple refereced in sets
    return (isset, (int(frame, 10), int(word, 10)))


def addr_bit2word(bitaddr):
    word = bitaddr // 32
    bit = bitaddr % 32
    return word, bit


def addr2str(addr, word, bit):
    # Make like .bits file: bit_00020b14_073_05
    # also similar to .db file: CLBLL_L.SLICEL_X0.CEUSEDMUX 01_39
    assert 0 <= bit <= 31
    return "%08x_%03u_%02u" % (addr, word, bit)


# matches lib/include/prjxray/xilinx/xc7series/block_type.h
block_type_i2s = {
    0: 'CLB_IO_CLK',
    1: 'BLOCK_RAM',
    2: 'CFG_CLB',
    # special...maybe should error until we know what it is?
    # 3: 'RESERVED',
}
block_type_s2i = {}
for k, v in block_type_i2s.items():
    block_type_s2i[v] = k


def addr2btype(base_addr):
    '''
    Convert integer address to block type

    Table 5-24: Frame Address Register Description
    Bit Index: [25:23]
    https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf
    "Valid block types are CLB, I/O, CLK ( 000 ), block RAM content ( 001 ), and CFG_CLB ( 010 ). A normal bitstream does not include type 011 ."
    '''
    block_type_i = (base_addr >> 23) & 0x7
    return block_type_i2s[block_type_i]


def specn():
    # ex: build/specimen_001
    specdir = os.getenv("SPECDIR")
    return int(re.match(".*specimen_([0-9]*)", specdir).group(1), 10)


def gen_fuzz_choices(nvals):
    next_p2_states = 2**math.ceil(math.log(nvals, 2))
    n = next_p2_states

    full_mask = 2**next_p2_states - 1

    choices = []
    invert_choices = []

    num_or = 1
    while n > 0:
        mask = 2**n - 1

        val = 0

        for offset in range(0, num_or, 2):
            shift = offset * next_p2_states // num_or
            val |= mask << shift

        choices.append(full_mask ^ val)
        invert_choices.append(val)

        n //= 2
        num_or *= 2

    choices.extend(invert_choices)

    return choices


def gen_fuzz_states(nvals):
    '''
    Generates an optimal encoding to solve single bits as quickly as possible

    tilegrid's initial solve for 4 bits works like this:
    Initial reference value of all 0s:
    0000
    Then one-hot for each:
    0001
    0010
    0100
    1000
    Which requires 5 samples total to diff these

    However, using correlation instead its possible to resolve n bits using ceil(log(n, 2)) + 1 samples
    With 4 positions it takes only 3 samples:
    0000
    0101
    1010
    '''

    choices = gen_fuzz_choices(nvals)
    spec_idx = specn() - 1
    if spec_idx < len(choices):
        bits = choices[spec_idx]
    else:
        next_p2_states = 2**math.ceil(math.log(nvals, 2))
        bits = random.randint(0, 2**next_p2_states)

    for i in range(nvals):
        mask = (1 << i)
        yield int(bool(bits & mask))


def add_bool_arg(parser, yes_arg, default=False, **kwargs):
    dashed = yes_arg.replace('--', '')
    dest = dashed.replace('-', '_')
    parser.add_argument(
        yes_arg, dest=dest, action='store_true', default=default, **kwargs)
    parser.add_argument(
        '--no-' + dashed, dest=dest, action='store_false', **kwargs)

