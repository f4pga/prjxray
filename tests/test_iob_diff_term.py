#!/usr/bin/env python3
# SPDX-License-Identifier: ISC
"""Exercise 030-iob's real tag generator without Vivado or a device database."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'iob_generate', ROOT / 'fuzzers/030-iob/generate.py')
generate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate)


class TestDiffTerm(unittest.TestCase):
    def tags(self, kind='IBUFDS', excluded=False, standard='LVDS_25'):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            (root / 'build/iobanks.txt').write_text('IOB_X0Y2,13\nIOB_X0Y4,13\n')
            (root / 'build/pudc_sites.csv').write_text(
                'tile\n' + ('LIOB33_X0Y1\n' if excluded else ''))
            (root / 'build/cmt_regions.csv').write_text(
                'IOB_X0Y2,LIOB33_X0Y1,CMT0\n'
                'IOB_X0Y4,LIOB33_X0Y3,CMT0\n'
                'IDELAYCTRL_X0Y0,HCLK_IOI3_X1Y0,CMT0\n')
            (root / 'iobank_vref.csv').write_text('')
            design = []
            for y, enabled in ((2, 0), (4, 1)):
                design.append(dict(site='IOB_X0Y%d' % y,
                                   pair_site='IOB_X0Y%d' % (y-1),
                                   tile='LIOB33_X0Y%d' % (y-1),
                                   type=kind, IOSTANDARD='"%s"' % standard,
                                   DIFF_TERM=enabled, IBUF_LOW_PWR=0,
                                   PULLTYPE='"NONE"'))
            (root / 'params.json').write_text(json.dumps(dict(tiles=design)))
            segmk = MagicMock()
            old = Path.cwd()
            try:
                os.chdir(root)
                with patch.dict(os.environ, FUZDIR=str(root)), \
                        patch.object(generate, 'Segmaker', return_value=segmk):
                    generate.main()
            finally:
                os.chdir(old)
            return [call.args for call in segmk.add_tile_tag.call_args_list
                    if call.args[1] == 'DIFF.DIFF_TERM']

    def test_both_states_are_tile_tags(self):
        self.assertEqual(self.tags(), [
            ('LIOB33_X0Y1', 'DIFF.DIFF_TERM', 0),
            ('LIOB33_X0Y3', 'DIFF.DIFF_TERM', 1)])

    def test_single_ended_input_is_not_tagged(self):
        self.assertEqual(self.tags(kind='IBUF'), [])

    def test_other_standard_is_not_inferred(self):
        self.assertEqual(self.tags(standard='TMDS_33'), [])

    def test_pudc_tile_remains_excluded(self):
        self.assertEqual(self.tags(excluded=True), [
            ('LIOB33_X0Y3', 'DIFF.DIFF_TERM', 1)])


if __name__ == '__main__':
    unittest.main()
