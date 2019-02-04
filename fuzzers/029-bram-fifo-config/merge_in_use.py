""" Merge IN_USE entries. 

Segmatch has trouble directly solving for RAM_IN_USE and FIFO_IN_USE.
Instead if solves for IN_USE (e.g. RAM_IN_USE or FIFO_IN_USE) and the FIFO_IN_USE bit.

This tool merges the 3 entries into 2 entries RAM_IN_USE and FIFO_IN_USE.


BRAM.RAMB18_Y0.FIFO_IN_USE 27_150
BRAM.RAMB18_Y0.IN_USE 27_100 27_99
BRAM.RAMB18_Y0.RAM_IN_USE !27_150

becomes

BRAM.RAMB18_Y0.FIFO_IN_USE 27_100 27_99 27_150
BRAM.RAMB18_Y0.RAM_IN_USE 27_100 27_99 !27_150

"""
import argparse

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('unmerged_db')

    args = parser.parse_args()

    site_parts = {}

    with open(args.unmerged_db) as f:
        for l in f:
            parts = l.strip().split(' ')

            feature = parts[0]
            bits = parts[1:]

            feature_parts = feature.split('.')

            assert feature_parts[0] == 'BRAM'
            assert feature_parts[1] in ('RAMB18_Y0', 'RAMB18_Y1')
            site = feature_parts[1]

            if site not in site_parts:
                site_parts[site] = {}

            site_parts[site][feature_parts[2]] = bits

    assert len(site_parts) == 2
    for site in site_parts:
        assert 'IN_USE' in site_parts[site]
        assert len(site_parts[site]) == 3

        for feature in site_parts[site]:
            if feature == 'IN_USE':
                continue

            print('BRAM.{site}.{feature} {bits}'.format(
                site=site,
                feature=feature,
                bits=' '.join(site_parts[site]['IN_USE'] + site_parts[site][feature])))

if __name__ == "__main__":
    main()
