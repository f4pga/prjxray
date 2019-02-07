#!/usr/bin/env python3

from datetime import datetime, timedelta

import argparse
import collections
import io
import os
import os.path
import re
import resource
import signal
import subprocess
import sys
import traceback

import junit_xml

secs_in_min = 60
secs_in_hour = 60 * secs_in_min


def pretty_timedelta_str(d):
    """Pretty print a time delta object.

    >>> pretty_timedelta_str(timedelta(seconds=2))
    '2s'

    >>> pretty_timedelta_str(timedelta(seconds=61))
    '1m01s'

    >>> pretty_timedelta_str(timedelta(seconds=125))
    '2m05s'

    >>> pretty_timedelta_str(timedelta(seconds=secs_in_hour * 5))
    '5h00m'

    Once we get to displaying hours, we don't bother displaying seconds.
    >>> pretty_timedelta_str(timedelta(seconds=secs_in_hour * 5 + 1))
    '5h00m'

    >>> pretty_timedelta_str(timedelta(
    ...   seconds=secs_in_hour * 5 + secs_in_min * 2 + 1))
    '5h02m'

    >>> pretty_timedelta_str(timedelta(seconds=secs_in_hour * 5.5))
    '5h30m'
    """
    assert isinstance(d, timedelta)
    ts = d.total_seconds()
    assert ts > 0, (d, ts)

    bits = []
    hours = int(ts / secs_in_hour)
    if hours > 0:
        bits.append("{}h".format(hours))
        ts -= hours * secs_in_hour

    mins = int(ts / secs_in_min)
    if mins > 0 or hours > 0:
        if hours > 0:
            bits.append("{:02d}m".format(mins))
        else:
            bits.append("{:d}m".format(mins))
        ts -= mins * secs_in_min

    if hours == 0:
        if mins > 0:
            bits.append("{:02d}s".format(int(ts)))
        else:
            bits.append("{:d}s".format(int(ts)))

    assert len(bits) > 0, d

    return "".join(bits)


class Logger:
    """Output a bunch of lines with a prefix.

    >>> l = Logger("fuzz", datetime(2001, 11, 1), 6)
    >>> l._now = lambda: datetime(2001, 11, 1, second=10)
    >>> l.log("Test!")
    fuzz   -   10s: Test!
    >>> l.log("Format {} {t}", [1,], {'t': 2})
    fuzz   -   10s: Format 1 2
    >>> l.log('''\\
    ... Line 1
    ... Line 2
    ... Line 3
    ... ''')
    fuzz   -   10s: Line 1
    fuzz   -   10s: Line 2
    fuzz   -   10s: Line 3
    """

    def __init__(self, fuzzer, time_start, padding):
        self.fuzzer = fuzzer + ' ' * (padding - len(fuzzer))
        self.time_start = time_start
        self.queue = collections.deque()

    def _now(self):
        return datetime.utcnow()

    def log(self, msg, args=None, kw=None, flush=True):
        """Queue a log message.

        This is safe to do in a signal handler where you can't do io.
        """
        if args is None:
            args = []
        if kw is None:
            kw = {}

        time_log = self._now()
        self.queue.append((time_log, msg, args, kw))
        if flush:
            self.flush()

    def flush(self):
        while len(self.queue) > 0:
            time_log, msg, args, kw = self.queue.popleft()
            self._output(time_log, msg, args, kw)

    def _output(self, time_log, msg, args, kw):
        running_for = time_log - self.time_start
        msg = msg.format(*args, **kw)

        log_prefix = "{:s} - {:s} - {:>5s}: ".format(
            time_log.isoformat(),
            self.fuzzer,
            pretty_timedelta_str(running_for),
        )

        msg = "\n".join(log_prefix + x for x in msg.splitlines())
        print(msg, flush=True)


def last_lines(f, num, blocksize=100):
    r"""Return n last lines in a file.

    >>> f = io.StringIO("")
    >>> last_lines(f, 100)
    ['']

    >>> f = io.StringIO("1\n2")
    >>> last_lines(f, 100)
    ['1', '2']

    >>> f = io.StringIO("11\n22\n33\n44\n55")
    >>> last_lines(f, 100)
    ['11', '22', '33', '44', '55']

    >>> f = io.StringIO("11\n22\n33\n44\n55")
    >>> last_lines(f, 100, 2)
    ['11', '22', '33', '44', '55']

    >>> f = io.StringIO("11\n22\n33\n44\n55")
    >>> last_lines(f, 100, 3)
    ['11', '22', '33', '44', '55']

    >>> f = io.StringIO("11\n22\n33\n44\n55")
    >>> last_lines(f, 2, 2)
    ['44', '55']

    >>> f = io.StringIO("11\n22\n33\n44\n55")
    >>> last_lines(f, 2, 3)
    ['44', '55']

    >>> f = io.StringIO("11\n22\n33\n44\n55")
    >>> last_lines(f, 2, 4)
    ['44', '55']

    >>> f = io.StringIO("1\n22\n3333333\n")
    >>> last_lines(f, 100, 3)
    ['1', '22', '3333333', '']

    """
    lines = collections.deque([''])
    # Seek to the end of the file
    f.seek(0, os.SEEK_END)
    fpos = f.tell()

    while len(lines) < (num + 1) and fpos > 0:
        bs = min(blocksize, fpos)
        fpos = fpos - bs
        f.seek(fpos)
        data = f.read(bs)

        while True:
            lpos = data.rfind('\n')
            lines[0] = data[lpos + 1:] + lines[0]
            if lpos == -1:
                break
            lines.insert(0, '')
            data = data[:lpos]

    if fpos == 0:
        lines.insert(0, '')

    return list(lines)[1:]


def get_usage():
    # This function only works if you have a signal handler for the
    # signal.SIGCHLD signal.
    raw_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    # 0   ru_utime    time in user mode (float)
    # 1   ru_stime    time in system mode (float)
    # 2   ru_maxrss   maximum resident set size
    #
    # These fields are always zero on Linux
    # 3   ru_ixrss    shared memory size
    # 4   ru_idrss    unshared memory size
    # 5   ru_isrss    unshared stack size
    return "User:{}s System:{}s".format(
        int(raw_usage.ru_utime),
        int(raw_usage.ru_stime),
    )


def get_load():
    """Return current load average.

    Values is average perecntage of CPU used over 1 minute, 5 minutes, 15
    minutes.
    """
    a1, a5, a15 = os.getloadavg()
    cpus = os.cpu_count()
    return a1 / cpus * 100.0, a5 / cpus * 100.0, a15 / cpus * 100.0


class PsTree:
    _pstree_features = None

    @classmethod
    def get_features(cls):
        if cls._pstree_features is None:
            cls._pstree_features = []
            for f in ['-T', '-l']:
                try:
                    subprocess.check_output(
                        "pstree {}".format(f),
                        stderr=subprocess.STDOUT,
                        shell=True,
                    )
                    cls._pstree_features.append(f)
                except subprocess.CalledProcessError:
                    continue
        return cls._pstree_features

    @classmethod
    def get(cls, pid):
        """Get processes under current one.

        Requires the pstree until be installed, otherwise returns empty string.
        """
        p = subprocess.Popen(
            "pstree {} {}".format(" ".join(cls.get_features()), pid),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            universal_newlines=True,
        )
        stdout, stderr = p.communicate()

        # Special case segfaults.
        if 'Segmentation fault' in stderr:
            stderr = ''
            stdout = '(result too big, pstree segfaulted.)'

        # If no error, just return stdout
        if not stderr:
            return stdout

        return "{}\n{}".format(stdout, stderr)


def should_run_submake(make_flags):
    """Check if make_flags indicate that we should execute things.

    See https://www.gnu.org/software/make/manual/html_node/Instead-of-Execution.html#Instead-of-Execution  # noqa

    If this is a dry run or question then we shouldn't execute or output
    anything.

    The flags end up as single letter versions in the MAKEFLAGS environment
    variable.

    >>> should_run_submake('')
    True

    The following flags are important;

     -n == --dry-run

    >>> should_run_submake('n')
    False
    >>> should_run_submake('n --blah')
    False
    >>> should_run_submake('--blah n')
    False
    >>> should_run_submake('--blah')
    True
    >>> should_run_submake('--random')
    True

     -q == --question

    >>> should_run_submake('q')
    False
    >>> should_run_submake('q --blah')
    False
    >>> should_run_submake('--blah q')
    False
    >>> should_run_submake('--blah')
    True
    >>> should_run_submake('--random')
    True

      Both --dry-run and --question

    >>> should_run_submake('qn')
    False
    >>> should_run_submake('nq')
    False
    >>> should_run_submake('--quiant')
    True
    """
    r = re.search(r'(?:^|\s)[^-]*(n|q)[^\s]*(\s|$)', make_flags)
    if not r:
        return True
    return not bool(r.groups()[0])


def main(argv):
    fuzzers_dir = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fuzzer", help="fuzzer to run")
    parser.add_argument(
        "--retries",
        type=int,
        default=5,
        help="Retry a failed fuzzer n times.",
    )
    args = parser.parse_args()

    # Setup the logger with flush=False, it should be safe to use in a signal
    # handler.
    fuzzer_length = max(len(f) for f in os.listdir(fuzzers_dir))
    logger = Logger(args.fuzzer, datetime.utcnow(), fuzzer_length)

    # Need a signal handler on SIGCHLD otherwise get_resource doesn't return
    # anything.
    signal.signal(signal.SIGCHLD, lambda sig, frame: None)

    fuzzer_dir = os.path.join(fuzzers_dir, args.fuzzer)
    assert os.path.exists(fuzzer_dir), fuzzer_dir

    fuzzer_logdir = os.path.join(fuzzer_dir, "logs")
    if not os.path.exists(fuzzer_logdir):
        os.makedirs(fuzzer_logdir)
    assert os.path.exists(fuzzer_logdir)

    exit_code = -1
    for retry_count in range(0, args.retries):
        logger.log('Running fuzzer attempt: {}', [retry_count])
        exit_code = run_fuzzer(
            args.fuzzer,
            fuzzer_dir,
            fuzzer_logdir,
            logger,
        )
        if exit_code <= 0:
            break
        logger.log('WARNING: Fuzzer failed!')

    return exit_code


def run_fuzzer(fuzzer_name, fuzzer_dir, fuzzer_logdir, logger):
    def log(msg, *a, **k):
        logger.log(msg, a, k, flush=True)

    make_cmd = os.environ.get('MAKE', 'make')
    make_flags = os.environ.get('MAKEFLAGS', '')
    # Should run things?
    if not should_run_submake(make_flags):
        return 0

    fuzzer_runok = os.path.join(fuzzer_dir, "run.ok")
    if os.path.exists(fuzzer_runok):
        last_modified = datetime.fromtimestamp(os.stat(fuzzer_runok).st_mtime)

        log(
            "Skipping as run.ok exists (updated @ {})",
            last_modified.isoformat())

        return 0

    time_start = datetime.utcnow()
    log("Starting @ {}", time_start.isoformat())

    running_msg = "Running {} -C {} run (with MAKEFLAGS='{}')".format(
        make_cmd,
        fuzzer_dir,
        make_flags,
    )
    log(running_msg)

    log_suffix = ".{}.log".format(time_start.isoformat())
    fuzzer_stdout = os.path.join(fuzzer_logdir, "stdout" + log_suffix)
    fuzzer_stderr = os.path.join(fuzzer_logdir, "stderr" + log_suffix)

    # Write header to stdout/stderr to make sure they match.
    for fname in [fuzzer_stdout, fuzzer_stderr]:
        with open(fname, "w") as fd:
            fd.write("Build starting @ {}\n".format(time_start.isoformat()))
            fd.write(running_msg)
            fd.write("\n")
            fd.write("-" * 75)
            fd.write("\n")
            fd.flush()
            os.fsync(fd)

    # Open the log files for appending
    stdout_fd = open(fuzzer_stdout, "a")
    stderr_fd = open(fuzzer_stderr, "a")

    # Play nice with make's jobserver.
    # See https://www.gnu.org/software/make/manual/html_node/POSIX-Jobserver.html#POSIX-Jobserver  # noqa
    if '--jobserver-fds' in make_flags:
        job_re = re.search('--jobserver-fds=([0-9]+),([0-9]+)', make_flags)
        assert job_re, make_flags
        job_rd, job_wr = job_re.groups()

        job_rd = int(job_rd)
        job_wr = int(job_wr)
        assert job_rd > 2, (job_rd, job_wr, make_flags)
        assert job_wr > 2, (job_rd, job_wr, make_flags)

        # Make sure the file descriptors exist..
        job_rd_fd = os.fdopen(int(job_rd), 'rb', 0)
        assert job_rd_fd
        job_wr_fd = os.fdopen(int(job_wr), 'rb', 0)
        assert job_wr_fd

    p = None
    try:
        p = subprocess.Popen(
            [make_cmd, '-C', fuzzer_dir, 'run'],
            stdin=None,
            stdout=stdout_fd,
            stderr=stderr_fd,
            # Make sure not to close the fds as make uses fd=(3,4) for process
            # control.
            close_fds=False)

        while True:
            try:
                retcode = p.wait(timeout=10)
                p = None
            except subprocess.TimeoutExpired:
                retcode = None

            if retcode is not None:
                break
            log(
                "Still running (1m:{:0.2f}%, 5m:{:0.2f}%, 15m:{:0.2f}%).\n{}",
                *get_load(),
                PsTree.get(p.pid),
            )
    except (Exception, KeyboardInterrupt, SystemExit):
        retcode = -1
        tb = io.StringIO()
        traceback.print_exc(file=tb)
        log(tb.getvalue())

    # Prevent Ctrl-C so we exit properly...
    old_sigint_handler = signal.getsignal(signal.SIGINT)

    def log_die(sig, frame):
        logger.log("Dieing!")

    signal.signal(signal.SIGINT, log_die)

    # Cleanup child process if they haven't already died.
    try:
        if p is not None:
            try:
                retcode = p.wait(1)
            except subprocess.TimeoutExpired:
                retcode = -1
                p.kill()
                p.wait()
                log("Warning: Killed program which should have been dead!")
    except Exception:
        tb = io.StringIO()
        traceback.print_exc(file=tb)
        log(tb.getvalue())

    # Wait for all children to finish.
    try:
        while True:
            log("Child finished: {}", os.waitpid(-1, 0))
    except ChildProcessError:
        pass

    log("Finishing ({}).", get_usage())

    time_end = datetime.utcnow()

    error_log = "\n".join(last_lines(open(fuzzer_stderr), 10000))
    success_log = "\n".join(last_lines(open(fuzzer_stdout), 100))

    # Find the next X_sponge_log.xml file name...
    for i in range(0, 100):
        tsfilename = os.path.join(fuzzer_logdir, '{}_sponge_log.xml'.format(i))
        if not os.path.exists(tsfilename):
            break

    test_case = junit_xml.TestCase(
        name=fuzzer_name,
        timestamp=time_start.timestamp(),
        elapsed_sec=(time_end - time_start).total_seconds(),
        stdout=success_log,
        stderr=error_log,
    )

    if retcode != 0:
        test_case.add_failure_info(
            'Fuzzer failed with exit code: {}'.format(retcode))

    with open(tsfilename, 'w') as f:
        ts = junit_xml.TestSuite(fuzzer_name, [test_case])
        junit_xml.TestSuite.to_file(f, [ts])

    if retcode != 0:
        test_case.add_failure_info(
            'Fuzzer failed with exit code: {}'.format(retcode), )

        # Log the last 10,000 lines of stderr on a failure
        log(
            """\
Failed @ {time_end} with exit code: {retcode}
--------------------------------------------------------------------------
{error_log}
--------------------------------------------------------------------------
Failed @ {time_end} with exit code: {retcode}
""",
            retcode=retcode,
            error_log=error_log,
            time_end=time_end.isoformat())

    else:

        # Log the last 100 lines of a successful run
        log(
            """\
Succeeded! @ {}
--------------------------------------------------------------------------
{}
--------------------------------------------------------------------------
Succeeded! @ {}
""", time_end.isoformat(), success_log, time_end.isoformat())

    logger.flush()
    signal.signal(signal.SIGINT, old_sigint_handler)
    return retcode


if __name__ == "__main__":
    if "--test" in sys.argv or len(sys.argv) == 1:
        import doctest
        doctest.testmod()
    else:
        sys.exit(main(sys.argv))
