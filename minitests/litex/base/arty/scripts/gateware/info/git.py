import binascii
import os
import subprocess
import sys

from migen.fhdl import *
from litex.soc.interconnect.csr import *


def git_root():
    if sys.platform == "win32":
        # Git on Windows is likely to use Unix-style paths (`/c/path/to/repo`),
        # whereas directories passed to Python should be Windows-style paths
        # (`C:/path/to/repo`) (because Python calls into the Windows API).
        # `cygpath` converts between the two.
        git = subprocess.Popen(
            "git rev-parse --show-toplevel",
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
        )
        path = subprocess.check_output(
            "cygpath -wf -",
            stdin=git.stdout,
        )
        git.wait()
        return path.decode('ascii').strip()
    else:
        return subprocess.check_output(
            "git rev-parse --show-toplevel",
            shell=True,
            cwd=os.path.dirname(__file__),
        ).decode('ascii').strip()


def git_commit():
    data = subprocess.check_output(
        "git rev-parse HEAD",
        shell=True,
        cwd=git_root(),
    ).decode('ascii').strip()
    return binascii.unhexlify(data)


def git_describe():
    return subprocess.check_output(
        "git describe --dirty",
        shell=True,
        cwd=git_root(),
    ).decode('ascii').strip()


def git_status():
    return subprocess.check_output(
        "git status --short",
        shell=True,
        cwd=git_root(),
    ).decode('ascii').strip()


class GitInfo(Module, AutoCSR):
    def __init__(self):
        commit = sum(
            int(x) << (i * 8) for i, x in enumerate(reversed(git_commit())))
        self.commit = CSRStatus(160)

        # FIXME: This should be a read-only Memory object
        #extradata = [ord(x) for x in "\0".join([
        #    "https://github.com/timvideos/HDMI2USB-misoc-firmware.git",
        #    git_describe(),
        #    git_status(),
        #    "",
        #    ])]
        #self.extradata = CSRStatus(len(extradata)*8)

        self.comb += [
            self.commit.status.eq(commit),
            #    self.extradata.status.eq(extradata),
        ]
