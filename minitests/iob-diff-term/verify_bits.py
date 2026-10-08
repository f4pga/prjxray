#!/usr/bin/env python3
# SPDX-License-Identifier: ISC
"""Extract HR DIFF_TERM feature bits from a controlled, route-once comparator.

Reject unrelated changes, inconsistent same-type tiles and a changed baseline.
ECC word 50 is derived frame data, not a configurable feature.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

def read_bits(path):
    result = set()
    for line in path.read_text().splitlines():
        match = re.fullmatch(r'bit_([0-9a-fA-F]{8})_(\d+)_(\d+)', line)
        if not match:
            raise ValueError('Unexpected bitread output: '+line)
        frame, word, bit = int(match[1], 16), int(match[2]), int(match[3])
        if word != 50:
            result.add((frame, word, bit))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference', type=Path, nargs='?', default=Path('.'))
    p.add_argument('--db', type=Path, required=True)
    a = p.parse_args()
    pins = json.loads((a.reference/'pins.json').read_text())
    part = pins['part'].rsplit('-', 1)[0]
    # Package name is not the tilegrid directory name.
    die = re.match(r'(xc7z\d+)', part)[1]
    grid = json.loads((a.db/die/'tilegrid.json').read_text())
    off = read_bits(a.reference/'off.bits')
    if off != read_bits(a.reference/'off-repeat.bits'):
        raise RuntimeError('Repeated baseline changed configuration bits')
    features, evidence, additions, removals = {}, [], set(), set()
    for i, pair in enumerate(pins['pairs']):
        on = read_bits(a.reference/f'pair{i}.bits')
        added, removed = on-off, off-on
        if not added and not removed:
            raise RuntimeError('DIFF_TERM changed no bits')
        name = pair['p']['tile']
        tile = grid[name]
        region = tile['bits']['CLB_IO_CLK']
        base = int(region['baseaddr'], 16)
        tags = []
        for state, changed in ((True, added), (False, removed)):
            for frame, word, bit in sorted(changed):
                if not (base <= frame < base+region['frames'] and
                        region['offset'] <= word < region['offset']+region['words']):
                    raise RuntimeError(f'DIFF_TERM also changes bits outside {name}: {frame:08x}/{word}/{bit}')
                tags.append(('' if state else '!')+f'{frame-base:02d}_{32*(word-region["offset"])+bit:02d}')
        tags.sort()
        feature = tile['type']+'.DIFF.DIFF_TERM'
        if feature in features and features[feature] != tags:
            raise RuntimeError('Same tile type has inconsistent DIFF_TERM mapping')
        features[feature] = tags
        evidence.append(dict(pair=i, tile=name, feature=feature, bits=tags,
                             added=len(added), removed=len(removed)))
        additions |= added
        removals |= removed
    if additions & removals:
        raise RuntimeError('Per-pair changes conflict')
    if read_bits(a.reference/'all.bits') != (off-removals)|additions:
        raise RuntimeError('All-on configuration is not the union of individual changes')
    inputs = sorted(a.reference.glob('*.bit'))
    result = dict(features=features, pairs=evidence,
                  source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                  repeated_baseline_identical=True, all_on_union_verified=True,
                  comparator_part=pins['part'], ecc_word_excluded=50)
    (a.reference/'mapping.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
