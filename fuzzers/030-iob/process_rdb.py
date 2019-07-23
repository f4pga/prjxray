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
            if ('.SSTL135' in l or '.LVCMOS' in l
                    or '.LVTTL' in l) and 'IOB_' in l:
                iostandard_lines.append(l)
            else:
                print(l.strip())

    sites = {}

    for l in iostandard_lines:
        feature = get_name(l)
        feature_parts = feature.split('.')
        site = get_site(l)
        iostandard = feature_parts[2]

        bits = parse_bits(l)
        bits = filter_bits(site, bits)

        if site not in sites:
            sites[site] = {}

        group = feature_parts[3]
        if group not in sites[site]:
            sites[site][group] = {}

        if group in ['DRIVE', 'SLEW']:
            enum = feature_parts[4]
            sites[site][group][(iostandard, enum)] = bits
        elif group in ['IN', 'IN_ONLY', 'IN_USE', 'OUT', 'STEPDOWN']:
            sites[site][group][(iostandard, None)] = bits
        else:
            assert False, group

    for site in sites:
        for iostandard, enum in sites[site]['DRIVE']:
            sites[site]['DRIVE'][(iostandard, enum)] |= sites[site]['OUT'][(
                iostandard, None)]

        for iostandard, enum in sites[site]['IN']:
            sites[site]['IN_ONLY'][(iostandard, enum)] -= sites[site]['IN'][(
                iostandard, enum)]

    common_bits = {}
    for site in sites:
        for group in sites[site]:
            if (site, group) not in common_bits:
                common_bits[(site, group)] = set()

            for bits in sites[site][group].values():
                common_bits[(site, group)] |= bits

    slew_in_drives = {}

    for site in sites:
        common_bits[(site, 'DRIVE')] -= common_bits[(site, 'SLEW')]
        common_bits[(site, 'DRIVE')] -= common_bits[(site, 'STEPDOWN')]
        common_bits[(site, 'IN_ONLY')] |= common_bits[(site, 'DRIVE')]
        common_bits[(site, 'IN_ONLY')] -= common_bits[(site, 'STEPDOWN')]

        for iostandard, enum in sites[site]['DRIVE']:
            slew_in_drive = common_bits[
                (site, 'SLEW')] & sites[site]['DRIVE'][(iostandard, enum)]
            if slew_in_drive:
                if (site, iostandard) not in slew_in_drives:
                    slew_in_drives[(site, iostandard)] = set()

                slew_in_drives[(site, iostandard)] |= slew_in_drive
                sites[site]['DRIVE'][(iostandard, enum)] -= slew_in_drive

            sites[site]['DRIVE'][(iostandard,
                                  enum)] -= common_bits[(site, 'STEPDOWN')]

    for site, iostandard in slew_in_drives:
        for _, enum in sites[site]['SLEW']:
            sites[site]['SLEW'][(iostandard,
                                 enum)] |= slew_in_drives[(site, iostandard)]

    for site in sites:
        del sites[site]['OUT']
        del sites[site]['IN_USE']

    for site in sites:
        for group in sites[site]:
            common_groups = {}

            # Merge features that are identical.
            #
            # For example:
            #
            #  IOB33.IOB_Y1.LVCMOS15.IN 38_42 39_41
            #  IOB33.IOB_Y1.LVCMOS18.IN 38_42 39_41
            #
            # Must be grouped.
            for (iostandard, enum), bits in sites[site][group].items():
                if bits not in common_groups:
                    common_groups[bits] = {
                        'IOSTANDARDS': set(),
                        'enums': set(),
                    }

                common_groups[bits]['IOSTANDARDS'].add(iostandard)
                if enum is not None:
                    common_groups[bits]['enums'].add(enum)

            for bits, v in common_groups.items():
                if v['enums']:
                    feature = 'IOB33.{site}.{iostandards}.{group}.{enums}'.format(
                        site=site,
                        iostandards='_'.join(sorted(v['IOSTANDARDS'])),
                        group=group,
                        enums='_'.join(sorted(v['enums'])),
                    )
                else:
                    feature = 'IOB33.{site}.{iostandards}.{group}'.format(
                        site=site,
                        iostandards='_'.join(sorted(v['IOSTANDARDS'])),
                        group=group,
                    )

                neg_bits = frozenset(
                    '!{}'.format(b)
                    for b in (common_bits[(site, group)] - bits))
                print(
                    '{} {}'.format(feature, ' '.join(sorted(bits | neg_bits))))


if __name__ == "__main__":
    main()
