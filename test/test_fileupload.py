# -*- coding: utf-8 -*-
''' Tests for the FileUpload wrapper. '''

import unittest
import sys, os.path
import bottle
from bottle import FileUpload, BytesIO, tob
import tempfile

class TestFileUpload(unittest.TestCase):
    def test_name(self):
        self.assertEqual(FileUpload(None, 'abc', None).name, 'abc')

    def test_raw_filename(self):
        self.assertEqual(FileUpload(None, None, 'x/x').raw_filename, 'x/x')

    def test_content_type(self):
        fu = FileUpload(None, None, None, {"Content-type": "text/plain"})
        self.assertEqual(fu.content_type, 'text/plain')

    def assertFilename(self, bad, good):
        fu = FileUpload(None, None, bad)
        self.assertEqual(fu.filename, good)
        
    def test_filename(self):
        self.assertFilename('with space', 'with-space')
        self.assertFilename('with more  \t\n\r space', 'with-more-space')
        self.assertFilename('with/path', 'path')
        self.assertFilename('../path', 'path')
        self.assertFilename('..\\path', 'path')
        self.assertFilename('..', 'empty')
        self.assertFilename('.name.', 'name')
        self.assertFilename('.name.cfg', 'name.cfg')
        self.assertFilename(' . na me . ', 'na-me')
        self.assertFilename('path/', 'empty')
        self.assertFilename(bottle.tob('ümläüts$'), 'umlauts')
        self.assertFilename(bottle.touni('ümläüts$'), 'umlauts')
        self.assertFilename('', 'empty')
        self.assertFilename('a'+'b'*1337+'c', 'a'+'b'*254)

    def test_preserve_case_issue_582(self):
        self.assertFilename('UpperCase', 'UpperCase')

    def test_save_buffer(self):
        fu = FileUpload(open(__file__, 'rb'), 'testfile', __file__)
        buff = BytesIO()
        fu.save(buff)
        buff.seek(0)
        self.assertEqual(fu.file.read(), buff.read())

    def test_save_file(self):
        fu = FileUpload(open(__file__, 'rb'), 'testfile', __file__)
        buff = tempfile.TemporaryFile()
        fu.save(buff)
        buff.seek(0)
        self.assertEqual(fu.file.read(), buff.read())

    def test_save_overwrite_lock(self):
        fu = FileUpload(open(__file__, 'rb'), 'testfile', __file__)
        self.assertRaises(IOError, fu.save, __file__)

    def test_save_dir(self):
        fu = FileUpload(open(__file__, 'rb'), 'testfile', __file__)
        dirpath = tempfile.mkdtemp()
        filepath = os.path.join(dirpath, fu.filename)
        fu.save(dirpath)
        self.assertEqual(fu.file.read(), open(filepath, 'rb').read())
        os.unlink(filepath)
        os.rmdir(dirpath)
