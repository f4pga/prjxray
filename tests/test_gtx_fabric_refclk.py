#!/usr/bin/env python3
# SPDX-License-Identifier: ISC
"""Regression tests for independently tagging the GTX fabric reference input."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import random
import re
import tempfile
import unittest
from unittest.mock import patch

FUZDIR = Path(__file__).resolve().parents[1] / 'fuzzers/064-gtx-channel-conf'


def load(name):
    spec = importlib.util.spec_from_file_location('gtx_' + name, FUZDIR / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, {'SEED': '1'}):
        spec.loader.exec_module(module)
    return module


class Recorder:
    def __init__(self, unused):
        self.tags = {}
        self.compiled = False
        self.written = False

    def add_site_tag(self, site, name, value):
        self.tags[site, name] = value

    def compile(self, bitfilter):
        self.compiled = True

    def write(self):
        self.written = True


class GTXFabricRefclkTest(unittest.TestCase):
    def make_top(self, seed):
        top = load('top')
        sites = [('GTX_CHANNEL_%d_X0Y0' % n, 'GTX_CHANNEL_%d' % n,
                  'GTXE2_CHANNEL_X0Y%d' % n, 'GTXE2_CHANNEL') for n in range(4)]
        with tempfile.TemporaryDirectory() as directory:
            old = os.getcwd()
            os.chdir(directory)
            try:
                verilog = io.StringIO()
                with patch.dict(os.environ, {'FUZDIR': str(FUZDIR)}), \
                        patch.object(top, 'gen_sites', return_value=iter(sites)), \
                        contextlib.redirect_stdout(verilog):
                    top.random.seed(seed)
                    top.main()
                return json.loads(Path('params.json').read_text()), verilog.getvalue()
            finally:
                os.chdir(old)

    def collect(self, primitives):
        generate = load('generate')
        recorder = Recorder('')
        with tempfile.TemporaryDirectory() as directory:
            old = os.getcwd()
            os.chdir(directory)
            try:
                Path('params.json').write_text(json.dumps(primitives))
                with patch.dict(os.environ, {'FUZDIR': str(FUZDIR)}), \
                        patch.object(generate, 'Segmaker', return_value=recorder), \
                        contextlib.redirect_stdout(io.StringIO()):
                    generate.main()
            finally:
                os.chdir(old)
        self.assertTrue(recorder.compiled)
        self.assertTrue(recorder.written)
        return recorder.tags

    def test_connection_and_tag_follow_randomized_state(self):
        seen = set()
        unused = False
        for seed in range(16):
            primitives, verilog = self.make_top(seed)
            used = [p for primitive in primitives for p in primitive['params'] if p['IN_USE']]
            self.assertEqual(verilog.count('.CPLLREFCLKSEL(3\'d7)'), len(used))
            tags = self.collect(primitives)
            for primitive in primitives:
                for params in primitive['params']:
                    state = params['GTGREFCLK_USED']
                    self.assertEqual(tags[params['site'], 'GTGREFCLK_USED'], state)
                    if not params['IN_USE']:
                        unused = True
                        self.assertFalse(state)
                        continue
                    seen.add(state)
                    instance = re.search(
                        r'\) ' + primitive['tile_type'].lower() + r' \((.*?)\n\);',
                        verilog, re.S).group(1)
                    ref = re.search(r'\.GTGREFCLK\((.*?)\)', instance).group(1)
                    self.assertEqual(ref != "1'b0", state)
                    if state:
                        self.assertRegex(ref, r'^lut_\d+_o$')
        self.assertEqual(seen, {False, True})
        self.assertTrue(unused)

    def test_legacy_params_have_no_fabric_reference(self):
        primitives, unused = self.make_top(1)
        for primitive in primitives:
            for params in primitive['params']:
                del params['GTGREFCLK_USED']
        tags = self.collect(primitives)
        for primitive in primitives:
            for params in primitive['params']:
                self.assertFalse(tags[params['site'], 'GTGREFCLK_USED'])


if __name__ == '__main__':
    unittest.main()
