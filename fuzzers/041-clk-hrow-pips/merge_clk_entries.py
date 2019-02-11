import argparse
import clk_table

def main():
    parser = argparse.ArgumentParser(description="Convert HCLK ROW/COLUMN definitions into HCLK pips.")
    parser.add_argument('in_segbit')
    parser.add_argument('piplist')
    parser.add_argument('out_segbit')

    args = parser.parse_args()

    hrow_outs = {}
    tile = None
    with open(args.in_segbit) as f:
        for l in f:
            parts = l.strip().split(' ')
            feature = parts[0]
            bits = ' '.join(parts[1:])

            tile1, dst, src = feature.split('.')
            if tile is None:
                tile = tile1
            else:
                assert tile == tile1

            n = int(src[-1])

            if dst not in hrow_outs:
                hrow_outs[dst] = {
                        'rows': {},
                        'columns': {},
                        }

            if src[-4:-1] == 'ROW':
                hrow_outs[dst]['rows'][n] = bits
            else:
                assert src[-7:-1] == 'COLUMN', src
                hrow_outs[dst]['columns'][n] = bits

    piplists = {}
    with open(args.piplist) as f:
        for l in f:
            tile, dst, src = l.strip().split('.')
            assert tile == 'CLK_HROW_BOT_R', tile

            if dst not in piplists:
                piplists[dst] = []

            piplists[dst].append(src)

    with open(args.out_segbit, 'w') as f:
        for dst in sorted(hrow_outs):
            for src in sorted(piplists[dst]):
                if src not in clk_table.CLK_TABLE:
                    continue

                row, column = clk_table.CLK_TABLE[src]

                if row not in hrow_outs[dst]['rows']:
                    continue

                if column not in hrow_outs[dst]['columns']:
                    continue

                print('CLK_HROW.{dst}.{inclk} {row_bits} {column_bits}'.format(
                    dst=dst,
                    inclk=src,
                    row_bits=hrow_outs[dst]['rows'][row],
                    column_bits=hrow_outs[dst]['columns'][column],
                    ), file=f)


if __name__ == "__main__":
    main()
