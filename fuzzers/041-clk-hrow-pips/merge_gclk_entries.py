import argparse

GCLKS = 32

def main():
    parser = argparse.ArgumentParser(description="Convert GCLK ROW/COLUMN definitions into GCLK pips.")
    parser.add_argument('in_segbit')
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

    with open(args.out_segbit, 'w') as f:
        for dst in hrow_outs:
            for gclk in range(GCLKS):
                row = gclk % 8
                column = int(gclk / 8)

                print('{tile}.{dst}.CLK_HROW_R_CK_GCLK{gclk} {row_bits} {column_bits}'.format(
                    tile=tile,
                    dst=dst,
                    gclk=gclk,
                    row_bits=hrow_outs[dst]['rows'][row],
                    column_bits=hrow_outs[dst]['columns'][column],
                    ), file=f)


if __name__ == "__main__":
    main()
