# -*- coding: utf-8 -*-
"""
eqn.py the equivalent of the eqn preprocessor

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

import sys
import re
from .eqn2latex import Eqn2Latex


class EqnError(Exception):
    pass

# delimiters should not be any of the following
invalid_delim = '^{}~"'


class InlineEqn(object):
    def __init__(self, start, end, eqncompiler=None):
        if start is None or len(start) != 1 or start in invalid_delim:
            raise EqnError('Invalid start delimiter')
        if end is None or len(end) != 1 or end in invalid_delim:
            raise EqnError('Invalid end delimiter')

        self._compiler = eqncompiler if eqncompiler else Eqn2Latex()
        self._regexp = re.compile(
            '([^{0}]*{0})(?P<eqn>[^{1}]+)({1})'.format(start, end))

    def compile(self, text):
        match = self._regexp.findall(text)
        if not match:
            return text
        subs = [''.join([case[0], self._compiler.translate(case[1]), case[2]])
                for case in match]
        return ''.join(subs)


eqnlatex = Eqn2Latex()


def eqn(input=sys.stdin, out=sys.stdout):
    delim = None
    nline = 0
    for line in input:
        nline += 1
        if not re.match('^\.EQ', line):
            out.writelines(delim.compile(line) if delim else line)
        else:
            line = input.readline()
            nline += 1
            if line.startswith('delim'):
                match = re.match('delim\s+(?P<start>\S)(?P<end>\S)', line)
                if not match:
                    raise EqnError('Wrong specification of delimiters for ' +
                                   'inline expressions at line {0}: "{1}"'
                                   .format(nline, line))
                delim = InlineEqn(match.group('start'),
                                  match.group('end'),
                                  eqnlatex)
                line = input.readline()
                nline += 1
                if not line.startswith('.EN'):
                    raise EqnError('Expected .EN')
                continue
            else:
                out.writelines('.EQ\n')
                lines = []
                while not re.match('^\.EN', line):
                    lines.extend(line)
                    line = input.readline()
                    nline += 1
                out.writelines(eqnlatex.translate(''.join(lines)) + '\n')
                out.writelines(line)


if __name__ == "__main__":
    import unittest as ut
    from io import StringIO

    class TestInlineExpressions(ut.TestCase):
        def setUp(self):
            self._compiler = InlineEqn('#', '#')

        def test_inline(self):
            code = 'Inlined as #x over 2#'
            result = self._compiler.compile(code)
            self.assertEqual(result, r'Inlined as #\frac{x}{2}#')

        def test_multiple(self):
            code = 'Inlined as #x over 2# and #x != y#'
            result = self._compiler.compile(code)
            self.assertEqual(result, r'Inlined as #\frac{x}{2}# and #x \ne y#')

    class TestPreprocessor(ut.TestCase):
        def test_delim(self):
            code = '''.EQ
delim ##
.EN
Some text #pi sup 2#'''
            input = StringIO(code)
            output = StringIO()
            eqn(input, output)
            result = output.getvalue()
            self.assertEqual(result, 'Some text #\pi^{2}#')

        @ut.expectedFailure
        def test_baddelim(self):
            code = '''.EQ
delim {0}{0}
.EN
Some text {0}pi sup 2{0}'''
            for char in invalid_delim:
                input = StringIO(code.format(char))
                output = StringIO()
                eqn(input, output)
                result = output.getvalue()
                self.assertEqual(result, 'Some text #\pi^{2}#')

        def test_eqnblock(self):
            code = '''Some text
.EQ
x over 2
.EN
and more'''
            input = StringIO(code)
            output = StringIO()
            eqn(input, output)
            result = output.getvalue()
            self.assertEqual(result, '''Some text
.EQ
\\frac{x}{2}
.EN
and more''')

    suite = ut.TestSuite()
    suite.addTest(ut.makeSuite(TestInlineExpressions))
    suite.addTest(ut.makeSuite(TestPreprocessor))
    runner = ut.TextTestRunner()
    runner.run(suite)
