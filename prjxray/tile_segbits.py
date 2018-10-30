from collections import namedtuple
from prjxray import bitstream
import enum


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
                self.segbits = read_segbits(f)

        for feature in self.segbits:
            sidx = feature.rfind('[')
            eidx = feature.rfind(']')

            if sidx != -1:
                assert eidx != -1

                base_feature = feature[:sidx]

                if base_feature not in self.feature_addresses:
                    self.feature_addresses[base_feature] = {}

                self.feature_addresses[base_feature][int(
                    feature[sidx + 1:eidx])] = feature

    def match_bitdata(self, bits, bitdata):
        """ Return matching features for tile bits data (grid.Bits) and bitdata.

        See bitstream.load_bitdata for details on bitdata structure.

        """

        for feature, segbit in self.segbits.items():
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

        if address == 0 and feature in self.segbits:
            for bit in self.segbits[feature]:
                yield bit
        else:
            for bit in self.segbits[self.feature_addresses[feature][address]]:
                yield bit

    def frames(self, bits):
        """ Iterate over frames this tile uses for a given bit location. """
        for query_bits in self.segbits.values():
            for bit in query_bits:
                yield bits.base_address + bit.word_column
