#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import clk_table


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags from design.txt.")
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

            if src in clk_table.CLK_TABLE:
                row, column = clk_table.CLK_TABLE[src]

                segmk.add_tile_tag(tile, '{}.HCLK_ENABLE_ROW{}'.format(dst, row), 1)
                segmk.add_tile_tag(tile, '{}.HCLK_ENABLE_COLUMN{}'.format(dst, column), 1)

                rows.remove(row)
                columns.remove(column)

                for row in rows:
                    segmk.add_tile_tag(tile, '{}.HCLK_ENABLE_ROW{}'.format(dst, row), 0)

                for column in columns:
                    segmk.add_tile_tag(tile, '{}.HCLK_ENABLE_COLUMN{}'.format(dst, column), 0)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
