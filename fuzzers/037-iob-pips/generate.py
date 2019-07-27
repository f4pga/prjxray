#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import os, re
import os.path


def bitfilter(frame, word):
    if frame < 28:
        return False
    return True


def main():
    segmk = Segmaker("design.bits")

    tiledata = {}
    pipdata = {}
    ignpip = set()

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'ioi3', 'lioi3.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []

            pipdata[tile_type].append((src, dst))

    with open(os.path.join(os.getenv('FUZDIR'), '..', 'piplist', 'build',
                           'ioi3', 'rioi3.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')
            if tile_type not in pipdata:
                pipdata[tile_type] = []

            pipdata[tile_type].append((src, dst))

    print("Loading tags from design.txt.")
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()
            if not tile.startswith('LIOI3') and not tile.startswith('RIOI3'):
                continue

            log = open("log.txt", "a")
            print(line, file=log)
            pip_prefix, _ = pip.split(".")
            tile_from_pip, tile_type = pip_prefix.split('/')

            _, src = src.split("/")
            _, dst = dst.split("/")
            pnum = int(pnum)
            pdir = int(pdir)

            if tile not in tiledata:
                tiledata[tile] = {
                    "type": tile_type,
                    "pips": set(),
                    "srcs": set(),
                    "dsts": set(),
                }

            tiledata[tile]["pips"].add((src, dst))
            tiledata[tile]["srcs"].add(src)
            tiledata[tile]["dsts"].add(dst)

            if pdir == 0:
                tiledata[tile]["srcs"].add(dst)
                tiledata[tile]["dsts"].add(src)

            if pnum == 1 or pdir == 0:
                print("Ignoring pip: {}".format(pip), file=log)
                ignpip.add((src, dst))

    for tile, pips_srcs_dsts in tiledata.items():
        tile_type = pips_srcs_dsts["type"]

        if tile_type.startswith('LIOI3'):
            tile_type = 'LIOI3'
        elif tile_type.startswith('RIOI3'):
            tile_type = 'RIOI3'

        pips = pips_srcs_dsts["pips"]

        for src, dst in pipdata[tile_type]:
            if (src, dst) in ignpip:
                pass
            if re.match(r'.*PHASER.*', src) or re.match(r'.*CLKDIV[PFB].*',
                                                        dst):
                pass
            elif (src, dst) in tiledata[tile]["pips"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 1)
            elif dst not in tiledata[tile]["dsts"]:
                segmk.add_tile_tag(tile, "%s.%s" % (dst, src), 0)

        internal_feedback = False

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    main()
