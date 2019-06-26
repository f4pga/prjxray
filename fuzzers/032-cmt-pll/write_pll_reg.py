import argparse

REGISTER_LAYOUT = {
        'CLKOUT1': [
            ('LOW_TIME', 6),
            ('HIGH_TIME', 6),
            ('RESERVED', 1),
            ('PHASE_MUX', 3),
            ],
        'CLKOUT2': [
            ('DELAY_TIME', 6),
            ('NO_COUNT', 1),
            ('EDGE', 1),
            ('MX', 2),
            ('FRAC_WF_R', 1),
            ('FRAC_EN', 1),
            ('FRAC', 3),
            ('RESERVED', 1),
            ],
        'DIVCLK': [
            ('LOW_TIME', 6),
            ('HIGH_TIME', 6),
            ('NO_COUNT', 1),
            ('EDGE', 1),
            ('RESERVED', 2),
            ],
        'LOCKREG1': [
            ('LKTABLE', 10, 20),
            ('LOCKREG1_RESERVED', 6, 0),
            ],
        'LOCKREG2': [
            ('LKTABLE', 10, 0),
            ('LKTABLE', 5, 30),
            ('LOCKREG2_RESERVED', 1, 0),
            ],
        'LOCKREG3': [
            ('LKTABLE', 10, 10),
            ('LKTABLE', 5, 35),
            ('LOCKREG3_RESERVED', 1, 0),
            ],
        'FILTREG1': [
            ('FILTREG1_RESERVED', 8, 0),
            ('TABLE', 1, 6),
            ('FILTREG1_RESERVED', 2, 8),
            ('TABLE', 2, 7),
            ('FILTREG1_RESERVED', 2, 10),
            ('TABLE', 1, 9),
            ],
        'FILTREG2': [
            ('FILTREG2_RESERVED', 4, 0),
            ('TABLE', 1, 0),
            ('FILTREG2_RESERVED', 2, 4),
            ('TABLE', 2, 1),
            ('FILTREG2_RESERVED', 2, 6),
            ('TABLE', 2, 3),
            ('FILTREG2_RESERVED', 2, 8),
            ('TABLE', 1, 5),
            ],
        'POWER_REG': [
            ('POWER_REG', 16),
            ]
        }

REGISTER_MAP = []

# 0x06 - 0x15
for output in [
        'CLKOUT5',
        'CLKOUT0',
        'CLKOUT1',
        'CLKOUT2',
        'CLKOUT3',
        'CLKOUT4',
        None,
        'CLKFBOUT']:
    if output is not None:
        REGISTER_MAP.append(('CLKOUT1', output))
        REGISTER_MAP.append(('CLKOUT2', output))
    else:
        REGISTER_MAP.append(None)
        REGISTER_MAP.append(None)

# 0x16
REGISTER_MAP.append(('DIVCLK', 'DIVCLK'))
# 0x17
REGISTER_MAP.append(None)
# 0x18-0x1A
REGISTER_MAP.append(('LOCKREG1', 'LOCKREG1'))
REGISTER_MAP.append(('LOCKREG2', 'LOCKREG2'))
REGISTER_MAP.append(('LOCKREG3', 'LOCKREG3'))

for _ in range(0x28-0x1A+1):
    REGISTER_MAP.append(None)

REGISTER_MAP.append(('POWER_REG', 'POWER_REG'))

for _ in range(0x4E-0x28+1):
    REGISTER_MAP.append(None)

# 0x4E - 0x4F
REGISTER_MAP.append(('FILTREG1', 'FILTREG1'))
REGISTER_MAP.append(('FILTREG2', 'FILTREG2'))


class RegisterAddress(object):
    def __init__(self, frame_offsets, bit_offset):
        self.frame_index = 0
        self.frame_offsets = frame_offsets
        self.bit_offset = bit_offset

    def next_bit(self):
        output = '{}_{}'.format(self.frame_offsets[self.frame_index], self.bit_offset)

        self.frame_index += 1
        if self.frame_index >= len(self.frame_offsets):
            self.frame_index = 0
            self.bit_offset += 1

        return output


def passthrough_non_register_segbits(seg_in):
    """ Filter input segbits file and capture register base offset.

    Some PLL bit ranges are documented registers in the PLL/MMCM dynamic
    reconfiguration iterface.  These features will be generated in
    output_registers.  In order for output_registers to function, it needs
    the starting bit offset of the register space, which is based off of
    base_offset_register segbit definition.

    Other features generated in fuzzing are passed through.

    """
    base_offset_register = 'CMT_UPPER_T.PLLE2.CLKOUT5_DIVIDE[1]'

    bit_offset = None
    with open(seg_in, 'r') as f:
        for l in f:
            if l.startswith(base_offset_register):
                parts = l.split()
                assert len(parts) == 2
                assert parts[0] == base_offset_register
                frame_offset, bit_index = map(int, parts[1].split('_'))

                assert frame_offset == 28
                assert bit_index > 3
                bit_offset = bit_index - 3

                continue

            parts = l.split()
            feature_parts = parts[0].split('.')

            if len(feature_parts) < 3:
                print(l.strip())
                continue

            if '[' not in feature_parts[2]:
                print(l.strip())
                continue

            base_feature = feature_parts[2].split('[')

            if base_feature[0] in [
                    'CLKOUT0_DIVIDE',
                    'CLKOUT1_DIVIDE',
                    'CLKOUT2_DIVIDE',
                    'CLKOUT3_DIVIDE',
                    'CLKOUT4_DIVIDE',
                    'CLKOUT5_DIVIDE',
                    'DIVCLK_DIVIDE',
                    'CLKFBOUT_MULT',
                    'CLKOUT0_DUTY_CYCLE',
                    ]:
                # These features are PLL registers, so ignore the base
                continue

            print(l.strip())

    assert bit_offset is not None
    return bit_offset


def output_registers(bit_offset):
    """ Output segbits for the known PLL register space.

    The first bit offset in the register space is required to generate this
    output.

    """
    reg = RegisterAddress(frame_offsets=[28, 29], bit_offset=bit_offset)

    for register in REGISTER_MAP:
        if register is None:
            for _ in range(16):
                reg.next_bit()
            continue

        layout, register_name = register

        layout_bits = REGISTER_LAYOUT[layout]

        simple_layout = len(layout_bits[0]) == 2

        for bit in range(16):
            if register_name != layout or layout in ['CLKOUT1', 'CLKOUT2']:
                print('CMT_UPPER_T.PLLE2.{}_{}[{}] {}'.format(
                    register_name, layout, bit, reg.next_bit()))
            else:
                print('CMT_UPPER_T.PLLE2.{}[{}] {}'.format(
                    register_name, bit, reg.next_bit()))

        if False:
            bit_count = 0
            if simple_layout:
                for field, width in layout_bits:
                    for bit in range(width):
                        print('CMT_UPPER_T.PLLE2.{}_{}_{}[{}] {}'.format(
                            register_name, layout, field, bit, reg.next_bit()))
                        bit_count += 1
            else:
                for field, width, start_bit in layout_bits:
                    for bit in range(width):
                        print('CMT_UPPER_T.PLLE2.{}[{}] {}'.format(
                            field, start_bit+bit, reg.next_bit()))
                        bit_count += 1

            assert bit_count == 16


def main():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument('--seg_in')

    args = parser.parse_args()

    bit_offset = passthrough_non_register_segbits(args.seg_in)

    output_registers(bit_offset)


if __name__ == "__main__":
    main()
