'''

Sample segdata.txt output (from 015-clbnffmux/specimen_001/segdata_clbll_r.txt):
seg 00020880_048
bit 30_00
bit 31_49
tag CLB.SLICE_X0.AFF.DMUX.CY 1
tag CLB.SLICE_X0.BFF.DMUX.BX 0

tilegrid.json provides tile addresses
'''

import os, json, re

XRAY_DATABASE = os.getenv("XRAY_DATABASE")
XRAY_DIR = os.getenv("XRAY_DIR")

BLOCK_TYPES = set(('CLB_IO_CLK', 'BLOCK_RAM', 'CFG_CLB'))


def recurse_sum(x):
    '''Count number of nested iterable occurances'''
    if type(x) in (str, bytearray):
        return 1
    if type(x) in (dict, ):
        return sum([recurse_sum(y) for y in x.values()])
    else:
        try:
            return sum([recurse_sum(y) for y in x])
        except TypeError:
            return 1


def json_hex2i(s):
    '''Convert a JSON hex literal into an integer (it can't store hex natively)'''
    # TODO: maybe just do int(x, 0)
    return int(s[2:], 16)


class segmaker:
    def __init__(self, bitsfile, verbose=False):
        self.verbose = verbose
        self.load_grid()
        self.load_bits(bitsfile)
        '''
        self.tags[site][name] = value
        Where:
        -site: ex 'SLICE_X13Y101'
        -name: ex 'CLB.SLICE_X0.AFF.DMUX.CY'
        '''
        self.site_tags = dict()
        self.tile_tags = dict()

        # output after compiling
        self.segments_by_type = None

    def load_grid(self):
        '''Load self.grid holding tile addresses'''
        print("Loading %s grid." % XRAY_DATABASE)
        with open("%s/database/%s/tilegrid.json" % (XRAY_DIR, XRAY_DATABASE),
                  "r") as f:
            self.grid = json.load(f)
        assert "segments" not in self.grid, "Old format tilegrid.json"

    def load_bits(self, bitsfile):
        '''Load self.bits holding the bits that occured in the bitstream'''
        '''
        Format:
        self.bits[base_frame][bit_wordidx] = set()
        Where elements are (bit_frame, bit_wordidx, bit_bitidx))
        bit_frame is a relatively large number forming the FDRI address
        base_frame is a truncated bit_frame address of related FDRI addresses
        0 <= bit_wordidx <= 100
        0 <= bit_bitidx < 31

        Sample bits input
        bit_00020500_000_08
        bit_00020500_000_14
        bit_00020500_000_17
        '''
        self.bits = dict()
        print("Loading bits from %s." % bitsfile)
        with open(bitsfile, "r") as f:
            for line in f:
                # ex: bit_00020500_000_17
                line = line.split("_")
                bit_frame = int(line[1], 16)
                bit_wordidx = int(line[2], 10)
                bit_bitidx = int(line[3], 10)
                base_frame = bit_frame & ~0x7f

                self.bits.setdefault(base_frame, dict()).setdefault(
                    bit_wordidx, set()).add(
                        (bit_frame, bit_wordidx, bit_bitidx))
        if self.verbose:
            print(
                'Loaded bits: %u bits in %u base frames' %
                (recurse_sum(self.bits), len(self.bits)))

    def add_site_tag(self, site, name, value):
        '''
        XXX: can add tags in two ways:
        -By site name
        -By tile name (used for pips?)
        Consider splitting into two separate data structures

        Record, according to value, if (site, name) exists

        Ex:
        self.addtag('SLICE_X13Y101', 'CLB.SLICE_X0.AFF.DMUX.CY', 1)
        Indicates that the SLICE_X13Y101 site has an element called 'CLB.SLICE_X0.AFF.DMUX.CY'
        '''
        self.site_tags.setdefault(site, dict())[name] = value

    def add_site_tag(self, tile, name, value):
        self.tile_tags.setdefault(tile, dict())[name] = value

    def compile(self, bitfilter=None):
        print("Compiling segment data.")
        tags_used = set()
        tile_types_found = set()

        self.segments_by_type = dict()

        def add_segbits(segments, segname, tiledata, bitfilter=None):
            '''
            Add and populate segments[segname]["bits"]
            Gives all of the bits that could exist for the space we are exploring
            Also add segments[segname]["tags"], but don't fill

            segments is a group related to a specific tile type (ex: CLBLM_L)
            It is composed of bits (possible bits) and tags (observed instances)
            segments[segname]["bits"].add(bitname)
            segments[segname]["tags"][tag] = value

            segname: FDRI address + word offset string
            tiledata: tilegrid info for this tile
            '''
            assert segname not in segments
            segment = segments.setdefault(
                segment, {
                    "bits": {},
                    "tags": dict()
                })

            for block_type, bitj in segment['bits'].items():
                segment["bits"][block_type] = set()

                base_frame = json_hex2i(bitj["baseaddr"])
                for wordidx in range(bitj["offset"],
                                     bitj["offset"] + bitj["height"]):
                    if base_frame not in self.bits:
                        continue
                    if wordidx not in self.bits[base_frame]:
                        continue
                    for bit_frame, bit_wordidx, bit_bitidx in self.bits[
                            base_frame][wordidx]:
                        bitname_frame = bit_frame - base_frame
                        bitname_bit = 32 * (
                            bit_wordidx - bitj["offset"]) + bit_bitidx
                        # some bits are hard to de-correlate
                        # allow force dropping some bits from search space for practicality
                        if bitfilter is None or bitfilter(bitname_frame,
                                                          bitname_bit):
                            bitname = "%02d_%02d" % (
                                bitname_frame, bitname_bit)
                            segment["bits"][block_type].add(bitname)

        '''
        XXX: wouldn't it be better to iterate over tags? Easy to drop tags
        For now, add a check that all tags are used
        '''
        for tilename, tiledata in self.grid.items():

            def add_tilename_tags():
                if not segname in segments:
                    add_segbits(
                        segments, segname, tiledata, bitfilter=bitfilter)

                for name, value in self.tile_tags[tilename].items():
                    tags_used.add((tilename, name))
                    tag = "%s.%s" % (tile_type_norm, name)
                    segments[segname]["tags"][tag] = value

            def add_site_tags():
                if not segname in segments:
                    add_segbits(
                        segments, segname, tiledata, bitfilter=bitfilter)

                if 'SLICE_' in site:
                    '''
                    Simplify SLICE names like:
                    -SLICE_X12Y102 => SLICE_X0
                    -SLICE_X13Y102 => SLICE_X1
                    '''
                    if re.match(r"SLICE_X[0-9]*[02468]Y", site):
                        sitekey = "SLICE_X0"
                    elif re.match(r"SLICE_X[0-9]*[13579]Y", site):
                        sitekey = "SLICE_X1"
                    else:
                        assert 0
                else:
                    assert 0, 'Unhandled site type'

                for name, value in self.site_tags[site].items():
                    tags_used.add((site, name))
                    tag = "%s.%s.%s" % (tile_type_norm, sitekey, name)
                    # XXX: does this come from name?
                    tag = tag.replace(".SLICEM.", ".")
                    tag = tag.replace(".SLICEL.", ".")
                    segments[segname]["tags"][tag] = value

            # ignore dummy tiles (ex: VBRK)
            if "bits" not in tiledata:
                continue

            tile_type = tiledata["type"]
            tile_types_found.add(tile_type)
            segments = self.segments_by_type.setdefault(tile_type, dict())
            '''
            Simplify names by simplifying like:
            -CLBLM_L => CLB
            -CENTER_INTER_R => CENTER_INTER
            '''
            tile_type_norm = re.sub("(LL|LM)?_[LR]$", "", tile_type)

            segname = "%s_%03d" % (
                # truncate 0x to leave hex string
                tiledata["baseaddr"][2:],
                tiledata["offset"])

            # process tile name tags
            if tilename in self.tile_tags:
                add_tilename_tags()

            # process site name tags
            for site in tiledata["sites"]:
                if site not in self.site_tags:
                    continue
                add_site_tags()

        if self.verbose:
            ntags = recurse_sum(self.tags)
            print("Used %u / %u tags" % (len(tags_used), ntags))
            print("Grid DB had %u tile types" % len(tile_types_found))
            assert ntags and ntags == len(tags_used)

    def write(self, suffix=None, roi=False):
        assert self.segments_by_type, 'No data to write'

        for segtype in self.segments_by_type.keys():
            if suffix is not None:
                filename = "segdata_%s_%s.txt" % (segtype.lower(), suffix)
            else:
                filename = "segdata_%s.txt" % (segtype.lower())

            print("Writing %s." % filename)

            with open(filename, "w") as f:
                segments = self.segments_by_type[segtype]
                for segname, segdata in sorted(segments.items()):
                    print("seg %s" % segname, file=f)
                    for bitname in sorted(segdata["bits"]):
                        print("bit %s" % bitname, file=f)
                    for tagname, tagval in sorted(segdata["tags"].items()):
                        print("tag %s %d" % (tagname, tagval), file=f)
