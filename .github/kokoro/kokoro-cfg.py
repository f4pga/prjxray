#!/usr/bin/env python3

db_full = """\
# Format: //devtools/kokoro/config/proto/build.proto

build_file: "symbiflow-prjxray-%(kokoro_type)s-db-%(part)s/.github/kokoro/db-full.sh"

timeout_mins: 4320

action {
  define_artifacts {
    regex: "**/*result*.xml"
    regex: "**/*.log"
    regex: "database/%(part)s/**"
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

for part in ['artix7', 'kintex7', 'zynq7']:
    with open("continuous-db-%s.cfg" % part, "w") as f:
        f.write(db_full % {
            'part': part,
            'kokoro_type': 'continuous',
        })

    with open("presubmit-db-%s.cfg" % part, "w") as f:
        f.write(db_full % {
            'part': part,
            'kokoro_type': 'presubmit',
        })
