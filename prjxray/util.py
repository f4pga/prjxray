import os
import re
from .roi import Roi
from .db import Database


def get_db_root():
    # Used during tilegrid db bootstrap
    ret = os.getenv("XRAY_DATABASE_ROOT", None)
    if ret:
        return ret

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


def gen_tile_bits(db_root, tilej, strict=False, verbose=False):
    '''
    For given tile yield
    (absolute address, absolute FDRI bit offset, tag)

    For each address space
    Find applicable files
    For each tag bit in those files, calculate absolute address and bit offsets

    Sample file names:
    segbits_clbll_l.db
    segbits_int_l.db
    segbits_bram_l.block_ram.db
    '''
    for block_type, blockj in tilej["bits"].items():
        baseaddr = int(blockj["baseaddr"], 0)
        bitbase = 32 * blockj["offset"]

        if block_type == "CLB_IO_CLK":
            fn = "%s/segbits_%s.db" % (db_root, tilej["type"].lower())
        else:
            fn = "%s/segbits_%s.db.%s" % (
                db_root, tilej["type"].lower(), block_type.lower())
        # tilegrid runs a lot earlier than fuzzers
        # may not have been created yet
        verbose and print("Check %s: %s" % (fn, os.path.exists(fn)))
        if strict:
            assert os.path.exists(fn)
        elif not os.path.exists(fn):
            continue

        with open(fn, "r") as f:
            for line in f:
                tag, bits, mode = parse_db_line(line)
                assert mode is None
                for bitstr in bits:
                    # 31_06
                    _bit_inv, (bit_addroff, bit_bitoff) = parse_tagbit(bitstr)
                    yield (baseaddr + bit_addroff, bitbase + bit_bitoff, tag)


def specn():
    # ex: build/specimen_001
    specdir = os.getenv("SPECDIR")
    return int(re.match(".*specimen_([0-9]*)", specdir).group(1), 10)


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
    bits = 0
    # First pass all 0's
    for speci in range(2, specn() + 1):
        # First pass do nothing
        # Second pass invert every other bit (mod 2)
        # Third pass invert blocks of two (mod 4)
        block_size = 2**(speci - 1)
        for maski in range(nvals):
            mask = (1 << maski)
            if maski % block_size < block_size / 2:
                bits ^= mask

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
