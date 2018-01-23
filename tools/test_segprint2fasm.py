import segprint2fasm

import unittest
import StringIO
import re


class TestStringMethods(unittest.TestCase):
    def check_segprint_fasm_equiv(self, segp_fn, fasm_fn):
        fout = StringIO.StringIO()
        segprint2fasm.run(open(segp_fn, 'r'), fout)
        fasm_out = fout.getvalue()

        fasm_ref = open(fasm_fn, 'r').read()

        def normalize(fasm):
            '''Remove all comments and sort'''
            ret = []
            for l in fasm.split('\n'):
                # Remove comments
                i = l.rfind('#')
                if i >= 0:
                    l = l[0:i]
                l = l.strip()
                if not l:
                    continue
                ret.append(l)
            return sorted(ret)

        fasm_out = normalize(fasm_out)
        fasm_ref = normalize(fasm_ref)
        self.assertEquals(fasm_ref, fasm_out)

    def test_lut_int(self):
        self.check_segprint_fasm_equiv(
            'test_data/lut_int/design.segp', 'test_data/lut_int.fasm')

    def test_ff_int(self):
        self.check_segprint_fasm_equiv(
            'test_data/ff_int/design.segp', 'test_data/ff_int.fasm')


if __name__ == '__main__':
    unittest.main()
