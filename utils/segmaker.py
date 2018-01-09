import os, json, re


class segmaker:
    def __init__(self, bitsfile):
        print("Loading %s grid." % os.getenv("XRAY_DATABASE"))
        with open("../../../database/%s/tilegrid.json" %
                  os.getenv("XRAY_DATABASE"), "r") as f:
            self.grid = json.load(f)

        self.bits = dict()
        self.tags = dict()

        print("Loading bits from %s." % bitsfile)
        with open(bitsfile, "r") as f:
            for line in f:
                line = line.split("_")
                bit_frame = int(line[1], 16)
                bit_wordidx = int(line[2], 10)
                bit_bitidx = int(line[3], 10)
                base_frame = bit_frame & ~0x7f

                if base_frame not in self.bits:
                    self.bits[base_frame] = dict()

                if bit_wordidx not in self.bits[base_frame]:
                    self.bits[base_frame][bit_wordidx] = set()

                self.bits[base_frame][bit_wordidx].add(
                    (bit_frame, bit_wordidx, bit_bitidx))

    def addtag(self, site, name, value):
        if site not in self.tags:
            self.tags[site] = dict()
        self.tags[site][name] = value

    def compile(self, bitfilter=None):
        print("Compiling segment data.")

        self.segments_by_type = dict()

        for tilename, tiledata in self.grid["tiles"].items():
            if "segment" not in tiledata:
                continue

            segdata = self.grid["segments"][tiledata["segment"]]

            if "baseaddr" not in segdata:
                continue

            if segdata["type"] not in self.segments_by_type:
                self.segments_by_type[segdata["type"]] = dict()
            segments = self.segments_by_type[segdata["type"]]

            tile_type = tiledata["type"]
            segname = "%s_%03d" % (
                segdata["baseaddr"][0][2:], segdata["baseaddr"][1])

            def add_segbits():
                if not segname in segments:
                    segments[segname] = {"bits": set(), "tags": dict()}

                    base_frame = int(segdata["baseaddr"][0][2:], 16)
                    for wordidx in range(
                            segdata["baseaddr"][1],
                            segdata["baseaddr"][1] + segdata["words"]):
                        if base_frame not in self.bits:
                            continue
                        if wordidx not in self.bits[base_frame]:
                            continue
                        for bit_frame, bit_wordidx, bit_bitidx in self.bits[
                                base_frame][wordidx]:
                            bitname_frame = bit_frame - base_frame
                            bitname_bit = 32 * (
                                bit_wordidx - segdata["baseaddr"][1]
                            ) + bit_bitidx
                            if bitfilter is None or bitfilter(bitname_frame,
                                                              bitname_bit):
                                bitname = "%02d_%02d" % (
                                    bitname_frame, bitname_bit)
                                segments[segname]["bits"].add(bitname)

            if tilename in self.tags:
                add_segbits()

                for name, value in self.tags[tilename].items():
                    tag = "%s.%s" % (
                        re.sub("(LL|LM)?_[LR]$", "", tile_type), name)
                    segments[segname]["tags"][tag] = value

            for site in tiledata["sites"]:
                if site not in self.tags:
                    continue

                add_segbits()

                if re.match(r"SLICE_X[0-9]*[02468]Y", site):
                    sitekey = "SLICE_X0"
                elif re.match(r"SLICE_X[0-9]*[13579]Y", site):
                    sitekey = "SLICE_X1"
                else:
                    assert 0

                for name, value in self.tags[site].items():
                    tag = "%s.%s.%s" % (
                        re.sub("(LL|LM)?_[LR]$", "", tile_type), sitekey, name)
                    tag = tag.replace(".SLICEM.", ".")
                    tag = tag.replace(".SLICEL.", ".")
                    segments[segname]["tags"][tag] = value

    def write(self, suffix=None, roi=False):
        for segtype in self.segments_by_type.keys():
            if suffix is not None:
                filename = "segdata_%s_%s.txt" % (segtype, suffix)
            else:
                filename = "segdata_%s.txt" % (segtype)

            print("Writing %s." % filename)

            with open(filename, "w") as f:
                segments = self.segments_by_type[segtype]
                if True:
                    for segname, segdata in sorted(segments.items()):
                        print("seg %s" % segname, file=f)
                        for bitname in sorted(segdata["bits"]):
                            print("bit %s" % bitname, file=f)
                        for tagname, tagval in sorted(segdata["tags"].items()):
                            print("tag %s %d" % (tagname, tagval), file=f)
                else:
                    print("seg roi", file=f)
                    for segname, segdata in sorted(segments.items()):
                        for bitname in sorted(segdata["bits"]):
                            print("bit %s_%s" % (segname, bitname), file=f)
                        for tagname, tagval in sorted(segdata["tags"].items()):
                            print(
                                "tag %s_%s %d" % (segname, tagname, tagval),
                                file=f)
