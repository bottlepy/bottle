# -*- coding: utf-8 -*-
import unittest
import base64
import sys, os.path, tempfile
from io import BytesIO

import bottle

class BaseMultipartTest(unittest.TestCase):
    def setUp(self):
        # if bottle.py < (3,11,0):
        #     self.skipTest("Not used")
        self.data = BytesIO()
        self.parts = None

    def write(self, *lines):
        for line in lines:
            self.data.write(bottle.tob(line))

    def parse(self, ctype=None, clen=-1, **kwargs):
        self.data.seek(0)
        h = bottle._parse_http_header(ctype or "multipart/form-data; boundary=foo")
        charset = h[0][1].get("charset", "utf8")
        boundary = h[0][1].get("boundary")
        parser = bottle._MultipartParser(self.data, boundary, clen, **kwargs)
        return list(parser.parse())

    def assertFile(self, name, filename, ctype, data):
        for part in self.parts:
            if part.name != name: continue
            self.assertEqual(part.filename, expected[0])
            self.assertEqual(part.content_type, expected[1])
            self.assertEqual(part.file.read(), bottle.tob(expected[2]))
            break
        else:
            self.fail("Field %s not found" % name)
    
    def assertForm(self, name, data):
        for part in self.parts:
            if part.name != name: continue
            self.assertEqual(part.filename, None)
            self.assertEqual(part.content_type, None)
            self.assertEqual(part.value, data)
            break
        else:
            self.fail("Field %s not found" % name)


class TestHeaderParser(BaseMultipartTest):

    def test_options_parser(self):
        parse = bottle._parse_http_header
        self.assertEqual(
            parse('form-data; name="Test"; filename="Test.txt"'),
            [('form-data', {"name": "Test", "filename": "Test.txt"})])
        self.assertEqual(parse('form-data; name="Test"; FileName="Te\\"st.txt"'),
        [('form-data', {"name": "Test", "filename": "Te\"st.txt"})])
        self.assertEqual(parse('form-data; name="Test"; filename="C:\\test\\bla.txt"'),
        [('form-data', {"name": "Test", "filename": "C:\\test\\bla.txt"})])
        self.assertEqual(parse('form-data; name="Test"; filename="\\\\test\\bla.txt"'),
        [('form-data', {"name": "Test", "filename": "\\\\test\\bla.txt"})])


class TestMultipartParser(BaseMultipartTest):

    def assertIterline(self, data, *expected, **options):
        self.assertEqual(
            list(bottle._MultipartParser(BytesIO(bottle.tob(data)), 'foo', **options)._lineiter()),
            [(bottle.tob(l), bottle.tob(nl)) for l,nl in expected])

    def test_iterlines(self):
        self.assertIterline('abc\ndef\r\nghi', ('abc\ndef','\r\n'), ('ghi', ''))

    def test_iterlines_limit(self):
        self.assertIterline('abc\ndef\r\nghi', ('abc\ndef','\r\n'), ('g', ''), content_length=10)
        self.assertIterline('abc\ndef\r\nghi', ('abc\ndef\r',''), content_length=8)

    def test_fuzzy_lineiter(self):
        """ Test all possible buffer sizes """
        minbuflen = 9 # boundary size of '--foo--\r\n'
        data = b'data\rdata\ndata\r\ndata\n\rdata\r\n'.replace(b'data', b'X'*minbuflen*2)
        lines = data.split(b"\r\n")[:-1]
        for tail in (b"", b"tail"):
            for buffer_size in range(minbuflen, len(data+tail)+1):
                splits = list(bottle._MultipartParser(
                    BytesIO(data+tail), 'foo',
                    buffer_size=buffer_size)._lineiter())
                partial = b""
                merged = []
                for part, nl in splits:
                    self.assertTrue(nl in (b"", b"\r\n"))
                    self.assertTrue(len(part) >= buffer_size or nl or part == tail)
                    partial += part
                    if nl:
                        merged.append(partial)
                        partial = b""
                self.assertEqual(merged, lines)
                self.assertEqual(tail, partial)

    def test_big_file(self):
        ''' If the size of an uploaded part exceeds memfile_limit,
            it is written to disk. '''
        test_file = 'abc'*1024
        boundary = '---------------------------186454651713519341951581030105'
        request = BytesIO(bottle.tob('\r\n').join(map(bottle.tob,[
        '--' + boundary,
        'Content-Disposition: form-data; name="file1"; filename="random.png"',
        'Content-Type: image/png', '', test_file, '--' + boundary,
        'Content-Disposition: form-data; name="file2"; filename="random.png"',
        'Content-Type: image/png', '', test_file + 'a', '--' + boundary,
        'Content-Disposition: form-data; name="file3"; filename="random.png"',
        'Content-Type: image/png', '', test_file*2, '--'+boundary+'--',''])))
        parts = list(bottle._MultipartParser(request, boundary, memfile_limit=len(test_file)).parse())
        p = {p.name: p for p in parts}
        try:
            self.assertEqual(p.get('file1').file.read(), bottle.tob(test_file))
            self.assertTrue(p.get('file1').is_buffered())
            self.assertEqual(p.get('file2').file.read(), bottle.tob(test_file + 'a'))
            self.assertFalse(p.get('file2').is_buffered())
            self.assertEqual(p.get('file3').file.read(), bottle.tob(test_file*2))
            self.assertFalse(p.get('file3').is_buffered())
        finally:
            for part in parts:
                part.close()

    def test_file_seek(self):
        ''' The file object should be readable withoud a seek(0). '''
        test_file = 'abc'*1024
        boundary = '---------------------------186454651713519341951581030105'
        request = BytesIO(bottle.tob('\r\n').join(map(bottle.tob,[
        '--' + boundary,
        'Content-Disposition: form-data; name="file1"; filename="random.png"',
        'Content-Type: image/png', '', test_file, '--' + boundary + '--',''])))
        p = list(bottle._MultipartParser(request, boundary).parse())
        self.assertEqual(p[0].file.read(), bottle.tob(test_file))
        self.assertEqual(p[0].value, test_file)

    def test_unicode_value(self):
        ''' The .value property always returns unicode '''
        test_file = 'abc'*1024
        boundary = '---------------------------186454651713519341951581030105'
        request = BytesIO(bottle.tob('\r\n').join(map(bottle.tob,[
        '--' + boundary,
        'Content-Disposition: form-data; name="file1"; filename="random.png"',
        'Content-Type: image/png', '', test_file, '--' + boundary + '--',''])))
        p = list(bottle._MultipartParser(request, boundary).parse())
        self.assertEqual(p[0].file.read(), bottle.tob(test_file))
        self.assertEqual(p[0].value, test_file)
        self.assertTrue(hasattr(p[0].value, 'encode'))

    def test_multiline_header(self):
        ''' HTTP allows headers to be multiline. '''
        test_file = bottle.tob('abc'*1024)
        test_text = u'Test text\n with\r\n ümläuts!'
        boundary = '---------------------------186454651713519341951581030105'
        request = BytesIO(bottle.tob('\r\n').join(map(bottle.tob,[
        '--' + boundary,
        'Content-Disposition: form-data;',
        '\tname="file1"; filename="random.png"',
        'Content-Type: image/png', '', test_file, '--' + boundary,
        'Content-Disposition: form-data;',
        ' name="text"', '', test_text,
        '--' + boundary + '--',''])))
        p = list(bottle._MultipartParser(request, boundary, charset='utf8').parse())
        self.assertEqual(p[0].name, "file1")
        self.assertEqual(p[0].file.read(), test_file)
        self.assertEqual(p[0].filename, 'random.png')
        self.assertEqual(p[1].name, "text")
        self.assertEqual(p[1].value, test_text)


class TestBrokenMultipart(BaseMultipartTest):

    def assertMPError(self, **ka):
        self.assertRaises(bottle.MultipartError, self.parse, **ka)

    def test_big_boundary(self):
        self.assertMPError(buffer_size=1024*3)

    def test_missing_content_type(self):
        self.assertMPError(ctype="")

    def test_unsupported_content_type(self):
        self.assertMPError(ctype='multipart/fantasy')

    def test_missing_boundary(self):
        self.assertMPError(ctype="multipart/form-data")

    def test_no_terminator(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc')
        self.assertMPError()

    def test_no_newline_after_content(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc', '--foo--')
        self.assertMPError()

    def test_no_newline_after_middle_content(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc', '--foo\r\n'
                   'Content-Disposition: form-data; name="file2"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc\r\n', '--foo--')
        parts = self.parse()
        self.assertEqual(len(parts), 1)
        self.assertTrue('name="file2"' in parts[0].value)

    def test_preamble_before_start_boundary(self):
        parts = self.write('Preamble\r\n', '--foo\r\n'
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc\r\n', '--foo--')
        parts = self.parse()
        self.assertEqual(parts[0].file.read(), bottle.tob('abc'))
        self.assertEqual(parts[0].filename, 'random.png')
        self.assertEqual(parts[0].name, 'file1')
        self.assertEqual(parts[0].content_type, 'image/png')

    def test_no_start_boundary(self):
        self.write('--bar\r\n','--nonsense\r\n'
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc\r\n', '--nonsense--')
        self.assertMPError()

    def test_disk_limit(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc'*1024+'\r\n', '--foo--')
        self.assertMPError(memfile_limit=0, disk_limit=1024)

    def test_mem_limit(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc'*1024+'\r\n', '--foo\r\n',
                   'Content-Disposition: form-data; name="file2"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc'*1024+'\r\n', '--foo--')
        self.assertMPError(mem_limit=1024*3)

    def test_invalid_header(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n',
                   'Bad header\r\n', '\r\n', 'abc'*1024+'\r\n', '--foo--')
        self.assertMPError()

    def test_content_length_to_small(self):
        self.write('--foo\r\n',
                   'Content-Disposition: form-data; name="file1"; filename="random.png"\r\n',
                   'Content-Type: image/png\r\n',
                   'Content-Length: 111\r\n', '\r\n', 'abc'*1024+'\r\n', '--foo--')
        self.assertMPError()

    def test_no_disposition_header(self):
        self.write('--foo\r\n',
                   'Content-Type: image/png\r\n', '\r\n', 'abc'*1024+'\r\n', '--foo--')
        self.assertMPError()

