#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import argparse
import hashlib
import os
import parse as format_parser
import subprocess
import sys

"""Module for generating the Info.md file found in the database directory."""

info_md_header = """
# Details

Last updated on {human_date} ({iso8601_date}).

Created using [Project X-Ray](https://github.com/SymbiFlow/prjxray) version [{commit_hash_short}](https://github.com/SymbiFlow/prjxray/commit/{commit_hash_long}).

Latest commit was;
```
{commit_latest}
```

"""

info_md_section = """

## Database for [{part_line}]({part_line}/)

### Settings

Created using following [settings/{part_line}.sh (sha256: {settings_sha256})](https://github.com/SymbiFlow/prjxray/blob/{commit_hash_long}/settings/{part_line}.sh)
```shell
{settings_contents}
```

### [Results]({part_line}/)

Results have checksums;

"""

info_md_file = " * [`{file_sha256}  ./{file_short_path}`](./{file_short_path})\n"


def sha256(s):
    m = hashlib.sha256()
    m.update(s)
    return m.hexdigest()


def sha256_file(p):
    return sha256(open(p, 'rb').read())


def run(c):
    o = subprocess.check_output(c, shell=True)
    return o.decode('utf-8').strip()


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--keep',
        default=False,
        action="store_true",
        help="""\
Keep the existing commit information.
""")
    args = parser.parse_args()

    info_md_filename = os.path.join('database', 'Info.md')
    assert os.path.exists(info_md_filename), info_md_filename

    info_md = []

    info_md.append(open('database/README.md').read())

    v = {}
    v['human_date'] = run('TZ=UTC date')
    v['iso8601_date'] = run('TZ=UTC date --iso-8601=seconds')
    if not args.keep:
        v['commit_latest'] = run('git log -1')
        v['commit_hash_short'] = run('git log -1 --pretty=%h')
        v['commit_hash_long'] = run('git log -1 --pretty=%H')
    else:
        with open(info_md_filename) as f:
            result = format_parser.parse(
                '{before}' + info_md_header + '{after}', f.read())
        assert result
        assert result['human_date']
        assert result['iso8601_date']
        v['commit_latest'] = result['commit_latest']
        v['commit_hash_short'] = result['commit_hash_short']
        v['commit_hash_long'] = result['commit_hash_long']

    info_md.append(info_md_header.format(**v))

    for part_line in sorted(os.listdir('database')):
        if part_line.startswith('.'):
            continue
        part_path = os.path.join('database', part_line)

        if not os.path.isdir(part_path):
            continue

        files = list(os.listdir(part_path))
        files.sort()

        settings_path = os.path.join('settings', part_line + '.sh')
        settings_raw = open(settings_path, 'rb').read()

        w = {}
        w['commit_hash_long'] = v['commit_hash_long']
        w['part_line'] = part_line
        w['settings_contents'] = settings_raw.decode('utf-8')
        w['settings_sha256'] = sha256(settings_raw)

        info_md.append(info_md_section.format(**w))

        files = []
        for dirpath, dirnames, filenames in os.walk(part_path):
            for f in filenames:
                files.append(os.path.join(dirpath, f))

        files.sort()
        for p in files:
            x = {}
            x['file_real_path'] = './' + p
            x['file_short_path'] = os.path.join(
                part_line, os.path.relpath(p, part_path))
            x['file_sha256'] = sha256_file(p)
            info_md.append(info_md_file.format(**x))

    with open(info_md_filename, 'w') as f:
        f.write("".join(info_md))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
