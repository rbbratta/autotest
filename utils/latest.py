#!/usr/bin/env python

#  Copyright(c) 2013 Intel Corporation.
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms and conditions of the GNU General Public License,
#  version 2, as published by the Free Software Foundation.
#
#  This program is distributed in the hope it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
#
#  The full GNU General Public License is included in this distribution in
#  the file called "COPYING".


from collections import namedtuple
from optparse import OptionParser
from subprocess import Popen, PIPE
from tempfile import mkstemp
import glob
import os
import sys

__author__ = 'rbbratta'


def get_input_filename(filename, results_dir, wildcard, previous):
    dirs = (
        os.path.join(results_dir, fname) for fname in os.listdir(results_dir))
    latests = sorted(dirs, key=os.path.getmtime)
    latest = latests[previous - 1]
    glob_path = os.path.join(latest, wildcard, "debug", filename)
    try:
        input_file_names = glob.glob(glob_path)
        input_file_names[0]
    except IndexError:
        raise ValueError("unable to glob files for %s" %
                         os.path.realpath(glob_path))
    return input_file_names

ColorizeProc = namedtuple(
    "ColorizeProc", ['input_file', 'proc', 'log_fd', 'log_file_name'])



def which(program):
    paths = (os.path.join(path, program) for path in os.environ.get(
        'PATH', '').split(os.pathsep))
    matches = (os.path.realpath(p) for p in paths if os.path.exists(
        p) and os.access(p, os.X_OK))
    return next(matches, '')

_have_ccze = False

def _gen_ccze_cmd_line(cmds):
    if _have_ccze:
        return cmds
    else:
        return ['cat']


def colorize(input_file_name):
    input_file = open(input_file_name)
    fd, log_file_name = mkstemp(dir="/dev/shm")
    ccze = Popen(
        _gen_ccze_cmd_line(
            ['ccze', '-A', '-o', 'nolookups', '-o', 'noscroll']),
        stdin=input_file, stdout=fd)
    return ColorizeProc(input_file, ccze, fd, log_file_name)


class Functions(object):

    @staticmethod
    def tail(filename, results_dir, wildcard, previous):
        input_file_name = get_input_filename(
            filename, results_dir, wildcard, previous)[0]
        sys.stderr.write(input_file_name + "\n")

        tail = Popen(['tail', '-F', input_file_name], stdout=PIPE)
        ccze = Popen(_gen_ccze_cmd_line(
            ['ccze', '-A', '-o', 'nolookups']), stdin=tail.stdout)
        try:
            ccze.wait()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def show(filename, results_dir, wildcard, previous):

        input_file_names = get_input_filename(
            filename, results_dir, wildcard, previous)
        procs = []
        try:
            for f in input_file_names:
                sys.stderr.write(f + "\n")
                # procs will fork and run in parallel
                procs.append(colorize(f))

            # reap all the procs
            for p in procs:
                p.proc.wait()
                p.input_file.close()
                os.close(p.log_fd)

            # reversed so we see the last file first
            log_file_names = [p.log_file_name for p in procs]
            log_file_names.sort(key=os.path.getmtime, reverse=True)
            less_proc = Popen(['less', '-MRX', '+G'] + log_file_names)
            less_proc.wait()
        finally:
            for p in procs:
                os.unlink(p.log_file_name)


def main():
    parser = OptionParser()
    parser.add_option('-c', action="store_true", default=False,
                      help="display client results")
    parser.add_option('-s', action="store_true", default=False,
                      help="display server results")
    parser.add_option('-f', action="store", default="client*.DEBUG",
                      help="filename glob to show, default client*.DEBUG for show, or client.0.log for tail")
    parser.add_option(
        '-p', action="store", default=0, type="int", dest="previous",
        help="use nth previous result, e.g. -1: next to last, -2: third to last")
    (options, args) = parser.parse_args()
    func = getattr(Functions, args[0])
    if args[0] == "tail":
        if options.c:
            options.f = "client.DEBUG"
        else:
            # when we tail we need client.0.log
            options.f = "client*.log"
    if options.s:
        options.results_dir = "/usr/local/autotest/results"
        options.wildcard = '*'
    else:
        options.results_dir = "results"
        options.wildcard = ''
    global _have_ccze
    _have_ccze = which('ccze')
    func(options.f, options.results_dir, options.wildcard, options.previous)


if __name__ == "__main__":
    main()
