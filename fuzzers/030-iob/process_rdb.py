""" IOB bits are more complicated than can be easily expressed to segmaker.

There are couple cases that need to be handled here:

- There are some bits that are always set for IN-only ports, but are cleared
  selectively for OUT and INOUT ports.
- There are bits per each IOSTANDARD, in addition to drive patterns.  These
  can be merged to provide unique "(IOSTANDARD, DRIVE)" bit sets.
"""
import argparse


def get_name(l):
    parts = l.strip().split(' ')
    return parts[0]


def get_site(l):
    return get_name(l).split('.')[1]


def parse_bits(l):
    parts = l.strip().split(' ')
    if parts[1] == '<0':
        return frozenset()
    else:
        return frozenset(parts[1:])


def filter_bits(site, bits):
    """ Seperate top and bottom bits.

    Some IOSTANDARD bits are tile wide, but really only apply to a half.
    It is hard to write a fuzzer for this, but it is easy to filter by site,
    and all bits appear to have a nice hard halve seperatation in the bitidx.
    """
    if site == 'IOB_Y0':
        min_bitidx = 64
        max_bitidx = 127
    elif site == 'IOB_Y1':
        min_bitidx = 0
        max_bitidx = 63
    else:
        assert False, site

    def inner():
        for bit in bits:
            bitidx = int(bit.split('_')[1])

            if bitidx < min_bitidx or bitidx > max_bitidx:
                continue

            yield bit

    return frozenset(inner())


def main():
    parser = argparse.ArgumentParser(
        description="Convert IOB rdb into good rdb."
        "")
    parser.add_argument('input_rdb')

    args = parser.parse_args()

    iostandard_lines = []
    with open(args.input_rdb) as f:
        for l in f:
            if ('.LVCMOS' in l or '.LVTTL' in l) and 'IOB_' in l:
                iostandard_lines.append(l)
            else:
                print(l.strip())

    common_in_only_bits = {
        'IOB_Y0': set(),
        'IOB_Y1': set(),
    }
    for l in iostandard_lines:
        if 'IN_OUT_COMMON' in l:
            common_in_only_bits[get_site(l)] |= parse_bits(l)

    for site in sorted(common_in_only_bits):
        print(
            'IOB33.{}.IN_ONLY'.format(site), ' '.join(
                common_in_only_bits[site]))

    iostandard_in = {}
    outs = {}
    drives = {}
    in_use = {}

    for l in iostandard_lines:
        name = get_name(l)
        site = get_site(l)
        iostandard = name.split('.')[2]

        if name.endswith('.IN_USE'):
            in_use[(site, iostandard)] = parse_bits(l)

    for l in iostandard_lines:
        name = get_name(l)
        site = get_site(l)
        iostandard = name.split('.')[2]

        if name.endswith('.IN'):
            in_bits = parse_bits(l) | in_use[(site, iostandard)]

            if in_bits not in iostandard_in:
                iostandard_in[in_bits] = []

            iostandard_in[in_bits].append((site, iostandard))

        if name.endswith('.OUT'):
            outs[(site,
                  iostandard)] = parse_bits(l) | in_use[(site, iostandard)]

        if '.DRIVE.' in name and '.IN_OUT_COMMON' not in name:
            drive = name.split('.')[-1]
            if (site, iostandard) not in drives:
                drives[(site, iostandard)] = {}

            if drive not in drives[(site, iostandard)]:
                drives[(site, iostandard)][drive] = {}

            drives[(site, iostandard)][drive] = filter_bits(
                site, parse_bits(l))

    common_in_bits = {
        'IOB_Y0': set(),
        'IOB_Y1': set(),
    }

    for bits in sorted(iostandard_in.keys()):
        sites, standards = zip(*iostandard_in[bits])

        site = set(sites)

        assert len(site) == 1, site
        site = site.pop()

        common_in_bits[site] |= bits

    for bits in sorted(iostandard_in.keys()):
        sites, standards = zip(*iostandard_in[bits])

        site = set(sites)

        assert len(site) == 1, site
        site = site.pop()

        neg_bits = set('!' + bit for bit in (common_in_bits[site] - bits))

        print(
            'IOB33.{}.{}.IN'.format(site, '_'.join(standards)),
            ' '.join(bits | neg_bits))

    iodrives = {}

    common_bits = {}

    for site, iostandard in drives:
        for drive in drives[(site, iostandard)]:
            combined_bits = drives[(site, iostandard)][drive] | outs[(
                site, iostandard)]

            if site not in common_bits:
                common_bits[site] = set(common_in_only_bits[site])

            common_bits[site] |= combined_bits

            if combined_bits not in iodrives:
                iodrives[combined_bits] = []

            iodrives[combined_bits].append((site, iostandard, drive))

    for bits in iodrives:
        sites, standards, drives = zip(*iodrives[bits])

        site = set(sites)

        assert len(site) == 1, site
        site = site.pop()

        neg_bits = set('!' + bit for bit in (common_bits[site] - bits))

        print(
            'IOB33.{}.{}.DRIVE.{}'.format(
                site, '_'.join(sorted(set(standards))), '_'.join(
                    sorted(set(drives)))), ' '.join(bits | neg_bits))


if __name__ == "__main__":
    main()
