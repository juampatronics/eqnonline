# -*- coding: utf-8 -*-
"""
tbllexer.py A tokenizer for the tbl language.

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

from ply import lex
from .Lexer import Lexer
from .tbldatalexer import TblDataLexer


class TblLexer(Lexer):
    tokens = (
        'CENTER', 'BOX', 'TAB', 'LPAREN', 'RPAREN', 'LINESIZE', 'FORMAT',
        'COMMA', 'SEMICOLON', 'DOT', 'TEXT', 'START', 'END', 'FONT', 'NUMBER',
        'VLINE', 'DBLVLINE', 'ENDFMTLINE', 'ALLBOX', 'EXPAND',
        )

    def __init__(self, **args):
        self.lexer = lex.lex(module=self, **args)
        self.tblcells = []
        self.datalexer = TblDataLexer()
        # we need to check whether the \n marks the start of a new format
        # line or not.
        self.newfmtline = False

    def get_tokens(self):
        return self.tokens + self.datalexer.tokens

    states = (
        ('format', 'exclusive'),
        ('body', 'inclusive'),
        )

    t_ANY_ignore = ' \t'

    def t_ANY_error(self, t):
        print("Illegal character '%s'", t.value[0])
        t.lexer.skip(1)

    def t_ANY_START(self, t):
        r'\.TS'
        t.lexer.push_state('format')
        return t

    def t_ANY_END(self, t):
        r'\.TE'
        t.lexer.pop_state()
        return t

    # Need to enforce a given order in which the regexps are checked.
    def t_format_CENTER(self, t):
        r'\bcenter\b'
        self.newfmtline = True
        return t

    def t_format_BOX(self, t):
        r'\bbox\b'
        self.newfmtline = True
        return t

    def t_format_ALLBOX(self, t):
        r'\ballbox\b'
        self.newfmtline = True
        return t

    def t_format_LINESIZE(self, t):
        r'\blinesize\s*\(\s*(?P<linesize>[^)]+)\s*\)'
        t.value = t.lexer.lexmatch.group('linesize').strip()
        self.newfmtline = True
        return t

    def t_format_COMMA(self, t):
        r','
        return t

    def t_format_LPAREN(self, t):
        r'\('
        return t

    def t_format_RPAREN(self, t):
        r'\)'
        return t

    # tab (marker) tells the lexer how to split cells,
    # so we need to adapt the lexer on runtime!
    def t_format_TAB(self, t):
        r'\btab\s*\(\s*(?P<tab>[^)]+)\s*\)'
        self.newfmtline = True
        tab = t.lexer.lexmatch.group('tab').strip()
        t.value = tab
        if len(tab) != 1:
            raise Exception('Invalid tab at line :' + t.lexer.lineno)
        self.datalexer.set_tab(tab)
        return t

    def t_format_SEMICOLON(self, t):
        r';'
        self.newfmtline = False
        return t

    def t_format_FORMAT(self, t):
        r'(\b([Ll]|[Rr]|[Cc]|[Ss]|[Nn]|[Aa]|[Tt])|\^|_)'
        self.newfmtline = True
        return t

    def t_format_FONT(self, t):
        r'(f*[bBiI]|f*cw|f*CW|p(?P<fsize>[+-]?[0-9]+))'
        return t

    def t_format_VLINE(self, t):
        r'\|+'
        self.newfmtline = True
        if len(t.value) > 1:
            t.type = 'DBLVLINE'
        return t

    # in troff, the units inches can be explicitly given
    t_format_NUMBER = r'\d+(\.[0-9+])*i*'

    def t_format_ENDFMTLINE(self, t):
        r'(\n+|\s*,\s*)'
        if self.newfmtline:
            self.newfmtline = False
            return t

    def t_format_DOT(self, t):
        r'\.'
        self.newfmtline = False
        t.lexer.pop_state()
        t.lexer.push_state('body')
        return t

    def t_body_TEXT(self, t):
        r'(.|\n)+(?=.TE)'
        return t

    # Define a rule so we can track line numbers
    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        if len(self.tblcells) > 0:
            return self.tblcells.pop(0)
        tok = self.lexer.token()
        if tok is not None and tok.type == 'TEXT':
            self.datalexer.input(tok.value)
            while True:
                newtok = self.datalexer.token()
                if newtok is None:
                    break
                self.tblcells.append(newtok)
            return self.tblcells.pop(0)
        return tok


if __name__ == "__main__":
    import unittest as ut

    expressions = ['''
        .TS
        tab (@);
        c l.
        1@User Console
        2@Monochromatic graphics terminal
        3@Touch screen
        4@High resolution display
        .TE''', '''.TS
        center,box,tab(|);
        c l.
        1|User Console
        2|Monochromatic graphics terminal
        3|Touch screen
        4|High resolution display
        .TE''', '''.TS
        tab(@);
        c || c c
        ^ ^ | c ||
        |l | l | n.
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
        .TE''', '''.TS
        allbox, tab(@);
        c c
        c l.
        first@some text \
        expanding several lines
        second@few words
        .TE''', '''.TS
        cB lI.
        first@some text
        _
        second@few words
        =
        third@few words
        .TE''']

    class TestLexer(ut.TestCase):
        def setUp(self):
            self.lexer = TblLexer()

        def test_expressions(self):
            for s in expressions:
                print(s)
                self.lexer.test(s)

    ut.main()
