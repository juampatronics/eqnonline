# -*- coding: utf-8 -*-
"""
tbl2html.py A tbl to html compiler.

Copyright (C) 2016
Juan Pablo de la Cruz Gutiérrez
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the Juan Pablo de la Cruz Gutierrez or juampatronics may
  be used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from .pytbl import TblTranslator


class _Tbl2Html(object):
    def __init__(self):
        self._init_params()

    def _init_params(self):
        self._header = False
        self._style = ''
        self._border = False
        self._cellfmt = []
        self._laststyle = None
        self._row = 0
        self._col = 0

    def tbl_tblformat(self, *args, meta=None):
        return ''

    def tbl_option(self, *args, meta=None):
        if args[0] == 'center':
            self._style += 'text-align: center;'
        elif args[0] == 'allbox':
            self._border = True
        elif args[0] == 'box':
            self._style += 'border: 1px solid black;'

    def tbl_cellfmt(self, *args, meta=None):
        param = args[0]
        if param[0].lower() == 'c':
            self._laststyle = 'text-alignment : center;'
        elif param[0].lower() == 'r':
            self._laststyle = 'text-alignment : right;'
        elif param[0].lower() == 'l':
            self._laststyle = 'text-alignment : left;'

        if 'font' in meta:
            font = meta['font']
            if 'italic' in font:
                self._laststyle += 'font-style: italic;'
            if 'bold' in font:
                self._laststyle += 'font-weight: bold;'
            if 'size' in font:
                self._laststyle += 'font-size: ' + font['size'] + 'px;'
        return self._laststyle

    def tbl_cellfmtline(self, *args, meta=None):
        self._cellfmt.append(args)

    def tbl_tblrow(self, *args, meta=None):
        html = ''
        if not self._header:
            if not self._border:
                # per default, tbl adds no border to the table
                self._style += 'border: none;'
            html = '<table style="' + self._style + '">'
            self._header = True
        html += '<tr>' + ' '.join(args) + '</tr>'
        self._row += 1
        self._col = 0
        return html

    def tbl_cell(self, *args, meta=None):
        if args[0] == '':
            # an empty cell correspond to the case where we want to span over
            # rows (\^).
            self._col += 1
            return ''
        html = '<td'
        stylerow = self._row if self._row < len(self._cellfmt) else -1
        if self._col < len(self._cellfmt[stylerow]):
            html += ' style="' + self._cellfmt[stylerow][self._col] + '"'
        if meta:
            if 'span' in meta:
                html += ' rowspan="' + str(meta['span']) + '"'
            if 'font' in meta:
                pass
        html += '>'
        self._col += 1
        return html + args[0] + '</td>' if len(args) == 1 \
            else html + ' '.join(args) + '</td>'

    def postproc(self):
        self._init_params()
        return '</table>'


class Tbl2Html(object):
    def __init__(self):
        self._translator = TblTranslator().from_class(_Tbl2Html())

    def translate(self, s):
        return self._translator.translate(s)

    def translate_file(self, filename):
        return self._translator.translate_file(filename)


if __name__ == "__main__":
    import unittest as ut
    import re

    class TblTests(ut.TestCase):
        def setUp(self):
            self._translator = Tbl2Html()
            return self

        def _run_tests(self, expressions, expected):
            for case, should in zip(expressions, expected):
                result = self._translator.translate(case)
                self.assertEqual(re.sub('\s+', '', result),
                                 re.sub('\s+', '', should))

        def test_basiccases(self):
            expressions = ['''.TS
                tab (@);
                c l.
                1@User Console
                2@Monochromatic graphics terminal
                3@Touch screen
                4@High resolution display
                .TE''', '''.TS
                center,box,tab(%);
                c l.
                1%User Console
                2%Monochromatic graphics terminal
                3%Touch screen
                4%High resolution display
                .TE''', '''.TS
                tab(|);
                c l
                r r.
                1|User Console
                2|Monochromatic graphics terminal
                3|Touch screen
                4|High resolution display
                .TE''', '''.TS
                tab(|);
                c c
                r r.
                vertically centered|User Console
                \^|Monochromatic graphics terminal
                \^|Touch screen
                \^|High resolution display
                .TE''']

            expected = ['''<table style="border: none;"><tr>
                <td style="text-alignment : center;">1</td>
                <td style="text-alignment : left;">User Console</td></tr>
                <tr><td style="text-alignment : center;">2</td>
                <td style="text-alignment : left;">
                Monochromatic graphics terminal</td></tr>
                <tr><td style="text-alignment : center;">3</td>
                <td style="text-alignment : left;">Touch screen</td></tr>
                <tr><td style="text-alignment : center;">4</td>
                <td style="text-alignment : left;">High resolution display
                </td></tr></table>
                ''',
                '''<table style="text-align: center;border: 1px solid black;
                border: none;"><tr><td style="text-alignment : center;">1</td>
                <td style="text-alignment : left;">User Console</td></tr>
                <tr><td style="text-alignment : center;">2</td>
                <td style="text-alignment : left;">
                Monochromatic graphics terminal</td></tr>
                <tr><td style="text-alignment : center;">3</td>
                <td style="text-alignment : left;">Touch screen</td></tr>
                <tr><td style="text-alignment : center;">4</td>
                <td style="text-alignment : left;">High resolution display</td>
                </tr></table>
                ''',
                '''<table style="border: none;"><tr>
                <td style="text-alignment : center;">1</td>
                <td style="text-alignment : left;">User Console</td></tr>
                <tr><td style="text-alignment : right;">2</td>
                <td style="text-alignment : right;">
                Monochromatic graphics terminal</td></tr>
                <tr><td style="text-alignment : right;">3</td>
                <td style="text-alignment : right;">Touch screen</td></tr>
                <tr><td style="text-alignment : right;">4</td>
                <td style="text-alignment : right;">
                High resolution display</td></tr></table>
                ''',
                '''<table style="border: none;"><tr>
                <td style="text-alignment : center;" rowspan="4">
                vertically centered</td> <td style="text-alignment : center;">
                User Console</td></tr> <tr>
                <td style="text-alignment : right;">
                Monochromatic graphics terminal</td></tr> <tr>
                <td style="text-alignment : right;">Touch screen</td></tr>
                <tr> <td style="text-alignment : right;">
                High resolution display</td></tr></table>''']

            self._run_tests(expressions, expected)

        def test_colexpansion(self):
            expressions = ['''.TS
                tab (@);
                c l.
                1@User Console
                2@Monochromatic graphics terminal
                3@Touch screen
                4@High resolution display
                .TE''']

            expected = ['''<table style="border: none;">
                <tr><td style="text-alignment : center;">1</td>
                <td style="text-alignment : left;">User Console</td></tr>
                <tr><td style="text-alignment : center;">2</td>
                <td style="text-alignment : left;">Monochromatic graphics
                terminal </td></tr>
                <tr><td style="text-alignment : center;">3</td>
                <td style="text-alignment : left;">Touch screen</td></tr>
                <tr><td style="text-alignment : center;">4</td>
                <td style="text-alignment : left;">High resolution display</td>
                </tr></table>''']

            self._run_tests(expressions, expected)

        def test_font(self):
            expressions = ['''.TS
                tab(|);
                cp12 rbi.
                first|second
                .TE''']
            expected = ['''<table style="border: none;"><tr>
                <td style="text-alignment : center;font-size: 12px;">first</td>
                <td style="text-alignment : right;font-style: italic;
                font-weight: bold;">second</td></tr></table>''']

            self._run_tests(expressions, expected)

    ut.main()
