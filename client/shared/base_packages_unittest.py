#!/usr/bin/python
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
import unittest
try:
    import autotest.common as common
except ImportError:
    import common
from autotest.client.utils import error
from autotest.client.shared import base_packages


class TestParseSSH(unittest.TestCase):

    def test_parse_ssh_path_raises_exception(self):
        for val in ["", "ssh://foo", "ssh:///bar"]:
            self.assertRaises(
                error.PackageUploadError, base_packages.parse_ssh_path, val)

    def test_parse_ssh_path(self):
        for val, expected in [
            ("ssh://foo/", ("foo", "/")),
            ("ssh://foo/bar", ("foo", "/bar")),
            ("ssh://user@foo/bar", ("user@foo", "/bar")),
            ("ssh://fcoe@10.0.0.12/srv/ftp", ("fcoe@10.0.0.12", "/srv/ftp"))
        ]:
            self.assertEqual(expected, base_packages.parse_ssh_path(val))


class TestParseTarball(unittest.TestCase):

    def test_parse_tarball_name(self):
        for val, expected in [
            ("dep-foo.tar.bz2", ("foo", "dep")),
            ("test-foo.tar.bz2", ("foo", "test")),
            ("client-foo.tar.bz2", ("foo", "client")),
            ("profiler-foo.tar.bz2", ("foo", "profiler")),
            ("tar-tar.tar.bz2", ("tar", "tar")),
            ("-tar.bz2.tar.bz2", ("tar.bz2", "")),
            ("tar.bz2-.tar.bz2", ("", "tar.bz2")),
            ("profiler-.tar.bz2", ("", "profiler")),
            ("   -   .tar.bz2", ("   ", "   ")),
        ]:
            self.assertEquals(
                expected, base_packages.BasePackageManager.parse_tarball_name(val))

    def test_parse_tarball_raise_valuerror(self):
        for val in [
            "",
            "bad.tar",
            "packages.checksum",
            "tar.bz2.tar.bz2",
            ".tar.bz2",
        ]:
            self.assertRaises(
                ValueError, base_packages.BasePackageManager.parse_tarball_name, val)


if __name__ == "__main__":
    unittest.main()
