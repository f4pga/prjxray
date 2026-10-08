#!/usr/bin/env python3
# SPDX-License-Identifier: ISC
"""Termination must not be forced off by the LVDS input-only feature."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'iob_process', ROOT/'fuzzers/030-iob/process_rdb.py')
process = importlib.util.module_from_spec(spec); spec.loader.exec_module(process)


class TestInputOnly(unittest.TestCase):
    def features(self, termination=True):
        lines = {'NORMAL': [], 'ONLY_DIFF': []}
        for standard, category in [('LVCMOS25', 'NORMAL'), ('LVDS_25', 'ONLY_DIFF')]:
            groups = {'IN_USE': '38_112', 'IN': '38_96', 'IN_DIFF': '38_96',
                      'IN_ONLY': '38_96 38_118', 'OUT': '38_100 39_97',
                      'DRIVE.I_FIXED': '38_100 39_97 38_112',
                      'SLEW.SLOW': '<const0>', 'STEPDOWN': '<const0>'}
            for group, bits in groups.items():
                lines[category].append('IOB33.IOB_Y0.%s.%s %s\n' % (standard, group, bits))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            process.process_features_sets(lines,
                frozenset(['38_100', '39_97']) if termination else frozenset())
        return dict(line.split(' ', 1) for line in output.getvalue().splitlines())

    def test_alias_relaxes_only_measured_termination_bits(self):
        result = self.features()
        alias = set(result['IOB33.IOB_Y0.LVDS_25.IN_ONLY'].split())
        legacy = set(result['IOB33.IOB_Y0.LVCMOS25_LVDS_25.IN_ONLY'].split())
        self.assertEqual(legacy - alias, {'!38_100', '!39_97'})
        self.assertFalse(alias - legacy)
        self.assertIn('38_118', alias)
        self.assertIn('!38_112', alias)

    def test_legacy_output_unchanged_without_measured_term(self):
        result = self.features(termination=False)
        self.assertNotIn('IOB33.IOB_Y0.LVDS_25.IN_ONLY', result)
        self.assertIn('!38_100', result['IOB33.IOB_Y0.LVCMOS25_LVDS_25.IN_ONLY'].split())


if __name__ == '__main__':
    unittest.main()
