# -*- coding: utf-8 -*-
"""
tbldatalexer.py

Copyright (C) 2016-2017
Juan Pablo de la Cruz Gutierrez
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

from collections import OrderedDict
import re
import inspect
from ply.lex import LexToken, LexError
from .Lexer import Lexer

DEFAULT_TAB = '@'

class TblDataLexer(Lexer):
    '''
    Lexer for the table contents. Instead of having one, bigger, nastier lexer,
    we decided to break it up into two simpler lexers, and combine them by
    composition.
    We follow conventions used in PLY:
        Name of members specifying a token should start with 't_'.
        Tokens are checked in the same order as declared.
        The lexer is instrumented through init() and token() methods, and
        provides with a self.tokens data member containing a list of all
        valid tokens.'''
    def __init__(self, tab=DEFAULT_TAB):
        self.lexpos = 0
        self.lineno = 0
        self.data = None
        self.tab = self._escape_char(tab)
        self._init_lut()

    def _escape_char(self, char):
        'escaped char so that we can match it with regexp'
        return '\\' + char if char in '|?*' else char

    def _init_lut(self):
        '''
        Initializes the lookup table of regular expressions defining the
        tokens. Regexps are tested in the very same order as defined.
        '''
        # Create a table of regexps to text. This is a slow option, but it
        # allows us to change the behavior of the lexer in runtime.
        members = inspect.getmembers(self)
        regexps = dict((name.split('_')[-1], regexp)
                       for name, regexp in members if name.startswith('t_'))
        # Keep only those who actually correspond to a token and compile the
        # corresponding regular expressions in the order they are given.
        self.regexps = OrderedDict()
        for toktype in self.tokens:
            self.regexps[toktype] = re.compile(regexps[toktype])

        self.ignore = None
        if hasattr(self, 't_ignore'):
            self.ignore = re.compile('(' +
                                     '|'.join([self._escape_char(char)
                                              for char in self.t_ignore]) +
                                     ')+')

    def set_tab(self, newtab):
        'sets the tab (separator token for the table cells) on runtime'
        self.tab = newtab
        self.t_TBLDATA = r'[^' + self._escape_char(self.tab) + '\n]+'
        self.t_ignore = ' \t' + self.tab
        self._init_lut()

    tokens = (
        'EMPTYCELL', 'EMPTYLINE', 'HLINE', 'DBLHLINE',
        'BLOCKSTART', 'BLOCKEND', 'NEWLINE', 'TBLDATA',
        )

    t_HLINE = r'_'
    t_DBLHLINE = r'='
    t_EMPTYCELL = '\\\\\^'
    t_BLOCKSTART = r'T{'
    t_BLOCKEND = r'}T'
    t_TBLDATA = r'[^' + DEFAULT_TAB + '\n]+'
    t_EMPTYLINE = r'\.sp'
    t_NEWLINE = '\n'
    t_ignore = ' \t' + DEFAULT_TAB
    # t_txtblock_TEXT = r'([^}]|\\})+'

    def input(self, data):
        self.lexpos = 0
        self.lineno = 0
        self.data = data

    def token(self):
        if self.data is None:
            raise LexError('No input given', '')
        if self.lexpos >= len(self.data):
            return None
        while self.lexpos < len(self.data):
            # Skip ignore tokens. See t_ignore
            match = self.ignore.match(self.data, self.lexpos)
            if match is not None:
                self.lexpos = match.end()
                continue
            # Get the next token and forward the lexer position accordingly
            for toktype in self.regexps:
                match = self.regexps[toktype].match(self.data, self.lexpos)
                if match is not None:
                    tok = LexToken()
                    tok.value = match.group()
                    tok.type = toktype
                    tok.lineno = self.lineno
                    tok.lexpos = self.lexpos
                    self.lexpos = match.end()
                    return tok
            raise LexError('Unknown token at ' + str(self.lexpos),
                           self.data[self.lexpos:])
        return None


if __name__ == "__main__":
    import unittest as ut
    cases = ['''
        Fuel@Substance@kcal/
        @@gram mol. wt.
        .sp
        Gases@Hydrogen@68.4
        \^@Methane@211
        \^@Butane@680
        \^@Ethane@368
        .sp
        Liquids@Benzene@82
        \^@Ethyl alcohol@328
        \^@Methyl alcohol@171
        ''', '''
        first@some text \
        expanding several lines
        second@few words
        ''', '''
        _@previous line underscored
        cell@=
        ''']

    class TestLexer(ut.TestCase):
        def setUp(self):
            self.lexer = TblDataLexer()

        def test_expressions(self):
            for s in cases:
                self.lexer.test(s)

    ut.main()
