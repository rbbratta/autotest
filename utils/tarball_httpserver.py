
"""Tarball HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

Modification of SimpleHTTPServer from Python stdlib.

Licensed under PSF.

"""
import tarfile
import sys


__version__ = "0.6"

__all__ = ["TarballHTTPRequestHandler"]

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import shutil
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    autotest_root = sys.argv[2]
except IndexError:
    sys.stderr.write("Usage: {0} PORT AUTOTEST_ROOT\n".format(sys.argv[0]))
    sys.exit(1)

class TarballHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "TarballHTTP/" + __version__
    BZ2 = 'application/x-bzip2'

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()


    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        if path.endswith(".tar.bz2"):
            src_dir, _ = path.split(".tar.bz2")
            # remove leading / in request_path
            try:
                # Always read in binary mode. Opening files in text mode may cause
                # newline translations, making the actual size of the content
                # transmitted *less* than the content-length!
                # create tarball here
                f = StringIO()
                t = tarfile.open("", "w:bz2", f)
                t.add(src_dir, "")
                t.close()
                length = f.tell()
                f.seek(0)
            except (IOError, OSError):
                self.send_error(404, "File not found")
                return None
            self.send_response(200)
            self.send_header("Content-type", self.BZ2)
            self.send_header("Content-Length", str(length))
            self.end_headers()
            return f



        else:
            f = None
            if os.path.isdir(path):
                if not self.path.endswith('/'):
                    # redirect browser - doing basically what apache does
                    self.send_response(301)
                    self.send_header("Location", self.path + "/")
                    self.end_headers()
                    return None
                return self.list_directory(path)
            else:
                # we might need to return null here in order to not break autotest
                self.send_error(404, "File not found")
                return None


    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = autotest_root
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            # skip "." and ".."
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)


def test(HandlerClass = TarballHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()