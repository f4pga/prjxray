import argparse

def main():
    parser = argparse.ArgumentParser("Form ZDB groups for BUFG.")
    
    parser.add_argument('bot_r')
    parser.add_argument('top_r')

    args = parser.parse_args()

    groups = {}

    with open(args.bot_r) as f:
        for l in f:
            parts = l.strip().split(' ')
            feature = parts[0]
            bits = parts[1:]
            tile_type, dst, src = feature.split('.')

            assert tile_type == "CLK_BUFG"

            if dst not in groups:
                groups[dst] = {}

            groups[dst][src] = bits

    for dst in groups:
        if len(groups[dst]) == 1:
            continue

        bits = set()
        zero_feature = None
        for src in groups[dst]:
            if groups[dst][src][0] == '<0':
                assert zero_feature is None
                zero_feature = src
            else:
                bits |= set(groups[dst][src])

        assert zero_feature is not None, dst

        print('{bits},{type}.{dst}.{src}'.format(
            bits=' '.join(sorted(bits)),
            type='CLK_BUFG',
            dst=dst,
            src=zero_feature))

if __name__ == "__main__":
    main()
