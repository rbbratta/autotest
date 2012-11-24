""" Parallel execution management """
import errno
import traceback

__author__ = """Copyright Andy Whitcroft 2006"""

from autotest.client.shared import error, utils
import sys, logging, os, gc, time
import cPickle as pickle
import cgitb


def fork_start(tmp, l):
    sys.stdout.flush()
    sys.stderr.flush()
    pid = os.fork()
    if pid:
        # Parent
        return pid

    try:
        try:
            # Negate the return value for os._ext(). False = os._exit(1),  True = os._exit(0)
            status = l()
            logging.debug("%s = l() for PID %d", status, os.getpid())
            if status is not None:
                status = int(not status)
            else:
                status = 0
        except error.AutotestError:
            raise
        except Exception, e:
            raise error.UnhandledTestError(e)
    except Exception, detail:
        try:
            try:
                logging.error('child process failed')
                # logging.exception() uses ERROR level, but we want DEBUG for
                # the traceback
                for line in cgitb.text(sys.exc_info()).splitlines():
                    logging.debug(line)
            finally:
                # note that exceptions originating in this block won't make it
                # to the logs
                output_dir = os.path.join(tmp, 'debug')
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                ename = os.path.join(output_dir, "error-%d" % os.getpid())
                pickle.dump(detail, open(ename, "w"))

                sys.stdout.flush()
                sys.stderr.flush()
        finally:
            # clear exception information to allow garbage collection of
            # objects referenced by the exception's traceback
            sys.exc_clear()
            gc.collect()
            logging.debug("Exception occurred, PID %d exiting with status 1", os.getpid())
            os._exit(1)
    else:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            logging.debug("PID %d exiting with status %d", os.getpid(), status)
            os._exit(status)


def _check_for_subprocess_exception(temp_dir, pid):
    ename = temp_dir + "/debug/error-%d" % pid
    if os.path.exists(ename):
        try:
            e = pickle.load(file(ename, 'r'))
        except ImportError:
            logging.error("Unknown exception to unpickle. Exception must be"
                          " defined in error module.")
            raise
        # rename the error-pid file so that they do not affect later child
        # processes that use recycled pids.
        i = 0
        while True:
            pename = ename + ('-%d' % i)
            i += 1
            if not os.path.exists(pename):
                break
        os.rename(ename, pename)
        raise e


def fork_poll(tmp, pid):
    try:
        (pid, status) = os.waitpid(pid, os.WNOHANG)
#        logging.debug("pid = %d status = %d", pid, status)
    except OSError as e:
        if e.errno == errno.ECHILD:
            return (None, None, None)
        else:
            return (None, None, e)
    if (0, 0) == (pid, status):
        return (None, None, None)
    else:
        # capture the exception so we can return with status as well
        try:
            _check_for_subprocess_exception(tmp, pid)
        except Exception as e:
            return (pid, status, e)

    if status:
        e = error.TestError("Test subprocess PID %d failed rc=%d" % (pid, status))
        return (pid, status, e)
    else:
        return (pid, status, None)


def fork_waitfor(tmp, pid):
    (pid, status) = os.waitpid(pid, 0)

    _check_for_subprocess_exception(tmp, pid)

    if status:
        raise error.TestError("Test subprocess PID %d failed rc=%d" % (pid, status))

def fork_waitfor_timed(tmp, pid, timeout):
    """
    Waits for pid until it terminates or timeout expires.
    If timeout expires, test subprocess is killed.
    """
    timer_expired = True
    poll_time = 2
    time_passed = 0
    while time_passed < timeout:
        time.sleep(poll_time)
        (child_pid, status) = os.waitpid(pid, os.WNOHANG)
        if (child_pid, status) == (0, 0):
            time_passed = time_passed + poll_time
        else:
            timer_expired = False
            break

    if timer_expired:
        logging.info('Timer expired (%d sec.), nuking pid %d', timeout, pid)
        utils.nuke_pid(pid)
        (child_pid, status) = os.waitpid(pid, 0)
        raise error.TestError("Test timeout expired, rc=%d" % (status))
    else:
        _check_for_subprocess_exception(tmp, pid)

    if status:
        raise error.TestError("Test subprocess failed rc=%d" % (status))

def fork_nuke_subprocess_and_children(tmp, pid):
    try:
        children = [int(p) for p in utils.get_children_pids(pid)]
    except error.CmdError:
        children = []
    # nuke the parent
    utils.nuke_pid(pid)
    # make sure all the children have died
    for c in children:
        utils.nuke_pid(c)
    _check_for_subprocess_exception(tmp, pid)

def fork_nuke_subprocess(tmp, pid):
    utils.nuke_pid(pid)
    _check_for_subprocess_exception(tmp, pid)
