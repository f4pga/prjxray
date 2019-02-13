#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import clk_table


def main():
    segmk = Segmaker("design.bits")
    table = clk_table.get_clk_table()

    print("Loading tags from design.txt.")

    active_gclks = {}
    active_clks = {}
    with open("design.txt", "r") as f:
        for line in f:
            tile, pip, src, dst, pnum, pdir = line.split()

            if not tile.startswith('CLK_HROW'):
                continue

            pip_prefix, pip = pip.split(".")
            tile_from_pip, tile_type = pip_prefix.split('/')
            assert tile == tile_from_pip
            _, src = src.split("/")
            _, dst = dst.split("/")

            rows = set(range(clk_table.CLK_TABLE_NUM_ROWS))
            columns = set(range(clk_table.CLK_TABLE_NUM_COLS))

            if src in table:
                row, column = table[src]

                segmk.add_tile_tag(
                    tile, '{}.HCLK_ENABLE_ROW{}'.format(dst, row), 1)
                segmk.add_tile_tag(
                    tile, '{}.HCLK_ENABLE_COLUMN{}'.format(dst, column), 1)

                rows.remove(row)
                columns.remove(column)

                for row in rows:
                    segmk.add_tile_tag(
                        tile, '{}.HCLK_ENABLE_ROW{}'.format(dst, row), 0)

                for column in columns:
                    segmk.add_tile_tag(
                        tile, '{}.HCLK_ENABLE_COLUMN{}'.format(dst, column), 0)

                if tile not in active_clks:
                    active_clks[tile] = set()

                active_clks[tile].add(src)

                if 'GCLK' in src:
                    if src not in active_gclks:
                        active_gclks[src] = set()

                    active_gclks[src].add(tile)

    tiles = sorted(active_clks.keys())

    for tile in active_clks:
        for src in table:
            if 'GCLK' not in src:
                active = src in active_clks[tile]
                segmk.add_tile_tag(tile, '{}_ACTIVE'.format(src), active)
            else:
                if src not in active_gclks:
                    segmk.add_tile_tag(tile, '{}_ACTIVE'.format(src), 0)
                elif tile in active_gclks[src]:
                    segmk.add_tile_tag(tile, '{}_ACTIVE'.format(src), 1)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
