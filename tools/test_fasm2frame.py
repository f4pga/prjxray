import fasm2frame

import unittest
import StringIO
import re


def frm2bits(txt):
    '''
    Convert output .frm file text to set of (frame addr, word #, bit index) tuples
    '''
    bits_out = set()
    for l in txt.split('\n'):
        l = l.strip()
        if not l:
            continue
        # 0x00020500 0x00000000,0x00000000,0x00000000,...
        addr, words = l.split(' ')
        addr = int(addr, 0)
        words = words.split(',')
        assert (101 == len(words))
        for wordi, word in enumerate(words):
            word = int(word, 0)
            for biti in xrange(32):
                val = word & (1 << biti)
                if val:
                    bits_out.add((addr, wordi, biti))
    return bits_out


def bitread2bits(txt):
    '''
    Convert .bits text file (ie bitread output) to set of (frame addr, word #, bit index) tuples
    '''
    bits_ref = set()
    for l in txt.split('\n'):
        l = l.strip()
        if not l:
            continue
        # bit_0002050b_004_14
        m = re.match(r'bit_(.{8})_(.{3})_(.{2})', l)
        addr = int(m.group(1), 16)
        word = int(m.group(2), 10)
        bit = int(m.group(3), 10)
        bits_ref.add((addr, word, bit))
    return bits_ref


class TestStringMethods(unittest.TestCase):
    def test_lut(self):
        '''Simple smoke test on just the LUTs'''
        fout = StringIO.StringIO()
        fasm2frame.run(open('test_data/lut.fasm', 'r'), fout)

    def bitread_frm_equals(self, frm_fn, bitread_fn):
        fout = StringIO.StringIO()
        fasm2frame.run(open(frm_fn, 'r'), fout)

        # Build a list of output used bits
        bits_out = frm2bits(fout.getvalue())

        # Build a list of reference used bits
        bits_ref = bitread2bits(open(bitread_fn, 'r').read())

        # Now check for equivilence vs reference design
        self.assertEquals(len(bits_ref), len(bits_out))
        self.assertEquals(bits_ref, bits_out)

    def test_lut_int(self):
        self.bitread_frm_equals(
            'test_data/lut_int.fasm', 'test_data/lut_int/design.bits')

    def test_ff_int(self):
        self.bitread_frm_equals(
            'test_data/ff_int.fasm', 'test_data/ff_int/design.bits')

    def test_sparse(self):
        '''Verify sparse equivilent to normal encoding'''
        frm_fn = 'test_data/lut_int.fasm'

        fout_sparse = StringIO.StringIO()
        fasm2frame.run(open(frm_fn, 'r'), fout_sparse, sparse=True)
        fout_sparse_txt = fout_sparse.getvalue()
        bits_sparse = frm2bits(fout_sparse_txt)

        fout_full = StringIO.StringIO()
        fasm2frame.run(open(frm_fn, 'r'), fout_full, sparse=False)
        fout_full_txt = fout_full.getvalue()
        bits_full = frm2bits(fout_full_txt)

        # Now check for equivilence vs reference design
        self.assertEquals(len(bits_sparse), len(bits_full))
        self.assertEquals(bits_sparse, bits_full)

        # Verify the full ROI is way bigger description
        # It will still be decent size though since even sparse occupies all columns in that area
        self.assertGreaterEqual(len(fout_full_txt), len(fout_sparse_txt) * 4)


if __name__ == '__main__':
    unittest.main()
