#!/usr/bin/env python3

# Header
contrib = ["""\
# Contributing to Project X-Ray
"""]

# Extract the "Contributing" section from README.md
found = False
for line in open('README.md'):
    if found:
        if line.startswith('# '):
            # Found the next top level header
            break
        contrib.append(line)
    else:
        if line.startswith('# Contributing'):
            found = True

# Footer
contrib.append(
    """\






----

This file is generated from [README.md](README.md), please edit that file then
run the `./.update-contributing.py`.

""")

open("CONTRIBUTING.md", "w").write("".join(contrib))
