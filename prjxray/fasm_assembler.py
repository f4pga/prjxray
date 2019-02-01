import fasm
from prjxray import bitstream
from prjxray import grid


class FasmLookupError(Exception):
    pass


class FasmInconsistentBits(Exception):
    pass


def init_frame_at_address(frames, addr):
    '''Set given frame to 0 if not initialized '''
    if not addr in frames:
        frames[addr] = [0 for _i in range(bitstream.FRAME_WORD_COUNT)]


class FasmAssembler(object):
    def __init__(self, db):
        self.db = db
        self.grid = db.grid()

        self.seen_tile = set()
        self.frames_in_use = set()

        self.frames = {}
        self.frames_line = {}

    def get_frames(self, sparse=False):
        if not sparse:
            frames = self.frames_init()
        else:
            # Even in sparse mode, zero all frames for any tile that is
            # setting a bit.  This handles the case where the tile has
            # multiple frames, but the FASM only specifies some of the frames.
            frames = {}
            for frame in self.frames_in_use:
                init_frame_at_address(frames, frame)

        for (frame_addr, word_addr, bit_index), is_set in self.frames.items():
            init_frame_at_address(frames, frame_addr)

            if is_set:
                frames[frame_addr][word_addr] |= 1 << bit_index

        return frames

    def frames_init(self):
        '''Set all frames to 0'''
        frames = {}

        for bits_info in self.grid.iter_all_frames():
            for coli in range(bits_info.bits.frames):
                init_frame_at_address(
                    frames, bits_info.bits.base_address + coli)

        return frames

    def frame_set(self, frame_addr, word_addr, bit_index, line):
        '''Set given bit in given frame address and word'''
        assert bit_index is not None

        key = (frame_addr, word_addr, bit_index)
        if key in self.frames:
            if self.frames[key] != 1:
                raise FasmInconsistentBits(
                    'FASM line "{}" wanted to set bit {} but was cleared by FASM line "{}"'
                    .format(
                        line,
                        key,
                        self.frames_line[key],
                    ))
            return

        self.frames[key] = 1
        self.frames_line[key] = line

    def frame_clear(self, frame_addr, word_addr, bit_index, line):
        '''Set given bit in given frame address and word'''
        assert bit_index is not None

        key = (frame_addr, word_addr, bit_index)
        if key in self.frames:
            if self.frames[key] != 0:
                raise FasmInconsistentBits(
                    'FASM line "{}" wanted to clear bit {} but was set by FASM line "{}"'
                    .format(
                        line,
                        key,
                        self.frames_line[key],
                    ))
            return

        self.frames[key] = 0
        self.frames_line[key] = line

    def enable_feature(self, tile, feature, address, line):
        gridinfo = self.grid.gridinfo_at_tilename(tile)

        def update_segbit(bit):
            '''Set or clear a single bit in a segment at the given word column and word bit position'''

            # TODO: How to determine if the feature targets BLOCK_RAM segment type?
            bits = gridinfo.bits[grid.BlockType.CLB_IO_CLK]

            seg_baseaddr = bits.base_address
            seg_word_base = bits.offset

            # Now we have the word column and word bit index
            # Combine with the segments relative frame position to fully get the position
            frame_addr = seg_baseaddr + bit.word_column
            # 2 words per segment
            word_addr = seg_word_base + bit.word_bit // bitstream.WORD_SIZE_BITS
            bit_index = bit.word_bit % bitstream.WORD_SIZE_BITS
            if bit.isset:
                self.frame_set(frame_addr, word_addr, bit_index, line)
            else:
                self.frame_clear(frame_addr, word_addr, bit_index, line)

        segbits = self.db.get_tile_segbits(gridinfo.tile_type)

        self.seen_tile.add(tile)

        db_k = '%s.%s' % (gridinfo.tile_type, feature)

        any_bits = False

        try:
            for bit in segbits.feature_to_bits(db_k, address):
                any_bits = True
                update_segbit(bit)
        except KeyError:
            raise FasmLookupError(
                "Segment DB %s, key %s not found from line '%s'" %
                (gridinfo.tile_type, db_k, line))

        if any_bits:
            # Mark all frames used by this tile as in use.
            bits = gridinfo.bits[grid.BlockType.CLB_IO_CLK]
            if tile not in self.seen_tile:
                for frame in segbits.frames(bits):
                    self.frames_in_use.add(frame)

    def parse_fasm_filename(self, filename):
        missing_features = []
        for line in fasm.parse_fasm_filename(filename):
            if not line.set_feature:
                continue

            line_strs = tuple(fasm.fasm_line_to_string(line))
            assert len(line_strs) == 1
            line_str = line_strs[0]

            parts = line.set_feature.feature.split('.')
            tile = parts[0]
            feature = '.'.join(parts[1:])

            # canonical_features flattens multibit feature enables to only
            # single bit features, which is what enable_feature expects.
            #
            # canonical_features also filters out features that are not enabled,
            # which are no-ops.
            for flat_set_feature in fasm.canonical_features(line.set_feature):
                address = 0
                if flat_set_feature.start is not None:
                    address = flat_set_feature.start

                try:
                    self.enable_feature(tile, feature, address, line_str)
                except FasmLookupError as e:
                    missing_features.append(str(e))

        if missing_features:
            raise FasmLookupError('\n'.join(missing_features))
