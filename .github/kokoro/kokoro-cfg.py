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

db_full = """\
# Format: //devtools/kokoro/config/proto/build.proto

build_file: "symbiflow-prjxray-%(kokoro_type)s-db-%(part)s/.github/kokoro/%(script)s"

timeout_mins: 4320

action {
  define_artifacts {
    # File types
    regex: "**/diff.html"
    regex: "**/diff.json"
    regex: "**/diff.patch"
    regex: "**/*result*.xml"
    regex: "**/*sponge_log.xml"
    regex: "**/fuzzers/*.tgz"
    # Whole directories
    # regex: "**/build/**" - Currently kokoro dies on number of artifacts.
    regex: "**/build/*.log"
    regex: "**/logs_*/**"
    # The database
    regex: "**/database/%(part)s/**"
    strip_prefix: "github/symbiflow-prjxray-%(kokoro_type)s-db-%(part)s/"
  }
}

env_vars {
  key: "KOKORO_TYPE"
  value: "%(kokoro_type)s"
}

env_vars {
  key: "KOKORO_DIR"
  value: "symbiflow-prjxray-%(kokoro_type)s-db-%(part)s"
}

env_vars {
  key: "XRAY_SETTINGS"
  value: "%(part)s"
}

env_vars {
  key: "XRAY_BUILD_TYPE"
  value: "full"
}
"""

for part in ['artix7', 'kintex7', 'zynq7', 'spartan7']:
    script = 'db-full.sh'

    with open("continuous-db-%s.cfg" % part, "w") as f:
        f.write(
            db_full % {
                'part': part,
                'kokoro_type': 'continuous',
                'script': script,
            })

    with open("presubmit-db-%s.cfg" % part, "w") as f:
        f.write(
            db_full % {
                'part': part,
                'kokoro_type': 'presubmit',
                'script': script,
            })
