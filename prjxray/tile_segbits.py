from collections import namedtuple
from prjxray import bitstream
from prjxray.grid import BlockType
import enum
import functools


class PsuedoPipType(enum.Enum):
    ALWAYS = 'always'
    DEFAULT = 'default'
    HINT = 'hint'


def read_ppips(f):
    ppips = {}

    for l in f:
        l = l.strip()
        if not l:
            continue

        feature, ppip_type = l.split(' ')

        ppips[feature] = PsuedoPipType(ppip_type)

    return ppips


Bit = namedtuple('Bit', 'word_column word_bit isset')


def parsebit(val):
    '''Return "!012_23" => (12, 23, False)'''
    isset = True
    # Default is 0. Skip explicit call outs
    if val[0] == '!':
        isset = False
        val = val[1:]
    # 28_05 => 28, 05
    seg_word_column, word_bit_n = val.split('_')

    return Bit(
        word_column=int(seg_word_column),
        word_bit=int(word_bit_n),
        isset=isset,
    )


def read_segbits(f):
    segbits = {}

    for l in f:
        # CLBLM_L.SLICEL_X1.ALUT.INIT[10] 29_14
        l = l.strip()

        if not l:
            continue

        parts = l.split(' ')

        assert len(parts) > 1

        segbits[parts[0]] = [parsebit(val) for val in parts[1:]]

    return segbits


class TileSegbits(object):
    def __init__(self, tile_db):
        self.segbits = {}
        self.ppips = {}
        self.feature_addresses = {}

        if tile_db.ppips is not None:
            with open(tile_db.ppips) as f:
                self.ppips = read_ppips(f)

        if tile_db.segbits is not None:
            with open(tile_db.segbits) as f:
                self.segbits[BlockType.CLB_IO_CLK] = read_segbits(f)

        if tile_db.block_ram_segbits is not None:
            with open(tile_db.block_ram_segbits) as f:
                self.segbits[BlockType.BLOCK_RAM] = read_segbits(f)

        for block_type in self.segbits:
            for feature in self.segbits[block_type]:
                sidx = feature.rfind('[')
                eidx = feature.rfind(']')

                if sidx != -1:
                    assert eidx != -1

                    base_feature = feature[:sidx]

                    if base_feature not in self.feature_addresses:
                        self.feature_addresses[base_feature] = {}

                    self.feature_addresses[base_feature][int(
                        feature[sidx + 1:eidx])] = (block_type, feature)

    def match_bitdata(self, block_type, bits, bitdata):
        """ Return matching features for tile bits data (grid.Bits) and bitdata.

        See bitstream.load_bitdata for details on bitdata structure.

        """

        if block_type not in self.segbits:
            raise StopIteration()

        for feature, segbit in self.segbits[block_type].items():
            match = True
            for query_bit in segbit:
                frame = bits.base_address + query_bit.word_column
                bitidx = bits.offset * bitstream.WORD_SIZE_BITS + query_bit.word_bit

                if frame not in bitdata:
                    match = not query_bit.isset
                    if match:
                        continue
                    else:
                        break

                found_bit = bitidx in bitdata[frame][1]
                match = found_bit == query_bit.isset

                if not match:
                    break

            if not match:
                continue

            def inner():
                for query_bit in segbit:
                    if query_bit.isset:
                        frame = bits.base_address + query_bit.word_column
                        bitidx = bits.offset * bitstream.WORD_SIZE_BITS + query_bit.word_bit
                        yield (frame, bitidx)

            yield (tuple(inner()), feature)

    def feature_to_bits(self, feature, address=0):
        if feature in self.ppips:
            return

        for block_type in self.segbits:
            if address == 0 and feature in self.segbits[block_type]:
                for bit in self.segbits[block_type][feature]:
                    yield bit
                return

        block_type, feature = self.feature_addresses[feature][address]
        for bit in self.segbits[block_type][feature]:
            yield bit
