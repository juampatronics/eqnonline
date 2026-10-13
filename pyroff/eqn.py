# -*- coding: utf-8 -*-
"""
eqn.py the equivalent of the eqn preprocessor

Copyright (C) 2016-2017
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


