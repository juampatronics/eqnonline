#-* -coding: utf-8 -*-
"""
tlexer.py A tokenizer for the tbl language.

Copyright (C) 2017
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

import re
import inspect
from ply.lex import LexToken, LexError
from functools import wraps
from collections import OrderedDict
from pdb import set_trace


class TblToken(LexToken):
    def __init__(self, toktype, value, lineno=0, pos=0):
        self.type = toktype
        self.value = value
        self.lexpos = pos
        self.lineno = lineno

    def __eq__(self, other):
        'Equality is position invariant'
        if self.type != other.type:
            return False
        if self.value != other.value:
            return False
        return True


tokens = {
    'layout': (
        'COMMA', 'CENTER', 'BOX', 'TAB', 'LPAREN', 'RPAREN', 'LINESIZE',
        'SEMICOLON','ALLBOX', 'DOUBLEBOX',
        ),
    'format': (
        'DOT', 'FONT', 'NUMBER', 'FORMAT', 'VLINE', 'DBLVLINE', 'ENDFMTLINE',
        ),
    'body': (
        'EMPTYCELL', 'BLOCKSTART', 'BLOCKEND', 'TEXT', 'NEWLINE', 'TAB',
        'TEXTBLOCK'
        )
    }


states = ('layout', 'format', 'body')

# default table element separator

class TblLexer(object):
    ignore = ' '

    def __init__(self, debug=False):
        self._debug = debug

        # create LUTs for regexps
        symbols = dict([sym for sym in inspect.getmembers(self)
                        if sym[0].startswith('t_')])
        self._callbacks = dict()
        for state in states:
            sttoken = OrderedDict()
            for token in tokens[state]:
                key = 't_' + state + '_' + token
                if key not in symbols:
                    raise LexError(
                        'Missing token function for "{}"'.format(token), '')
                if type(symbols[key]) == str:
                    sttoken[token] = self._token_from_regexp(symbols[key],
                                                             token)
                else:
                    sttoken[token] = self._token_from_method(symbols[key],
                                                             token)
            self._callbacks[state] = sttoken

    def _token_from_regexp(self, string, typename):
        '''Factory method that returns a closure that checks wether the regexp
           matches, and if so, returns the next token. Otherwise None.'''
        regexp = re.compile(string)
        context = self

        def _token(data):
            match = regexp.match(data)
            if match:
                t = TblToken(typename, match.group())
                t.lineno = self._line
                t.lexpos = context._pos
                t.lexmatch = match
                context._pos += match.end()
                return t
            return None
        _token.__name__ = typename
        _token.__doc__ = string
        return _token

    def _token_from_method(self, method, typename):
        func = self._token_from_regexp(method.__doc__, typename)

        @wraps(func)
        def _tokenmethod(data):
            tok = func(data)
            return method(tok) if tok else None
        return _tokenmethod

    def _set_tab(self, tab=r'\t'):
        'Sets the separator token for the table elements dynamically.'
        if tab in '\\|+.?[]()':
            tab = '\\' + tab
        self._callbacks['body']['TEXT'] = \
                self._token_from_regexp(r'[^' + tab + r'\n]+', 'TEXT')
        self._callbacks['body']['TAB'] = self._token_from_regexp(tab, 'TAB')

    def input(self, data):
        'Sets the input text and initializes the lexer.'
        if type(data) != str:
            raise LexError('Invalid input: ' + data, '')
        self._current_state = ('layout', 'format', 'body')
        self._first_token = True
        self._set_tab('\t')
        self._tab = '\t'
        self._data = data
        self._line = 0
        self._pos = 0

    def token(self):
        'Returns the next token in the stream. If none left returns None.'
        if self._pos >= len(self._data):
            return None
        while self._pos < len(self._data):
            if self._data[self._pos] in self.ignore:
                self._pos += 1
            else:
                break

        while self._pos < len(self._data):
            for state in self._current_state:
                for cb in self._callbacks[state]:
                    tok = self._callbacks[state][cb](self._data[self._pos:])
                    if tok is not None:
                        if self._first_token:
                            self._current_state = (state,)
                            self._first_token = False

                        if tok.type == 'SEMICOLON':
                            self._current_state = ('format', 'body')
                        elif tok.type == 'DOT' or state == 'body':
                            self._current_state = ('body',)
                        if state == 'body':
                            if tok.type in ['TAB', 'NEWLINE','BLOCKEND']:
                                # ignore and return next element in the table
                                return self.token()
                            if tok.type == 'BLOCKSTART':
                                tok = self._callbacks[state]['TEXTBLOCK'](
                                                    self._data[self._pos:])
                                tok.type = 'TEXT'
                        if self._debug:
                            print('>>> tok = ', tok)
                        return tok
            raise LexError('Unexpected token {} at line {}'.format(
                self._data[self._pos:], self._line), '')

    t_layout_CENTER = r'\bcenter\b'
    t_layout_ALLBOX = r'\ballbox\b'
    t_layout_DOUBLEBOX = r'\bdoublebox\b'
    t_layout_BOX = r'\bbox\b'
    t_layout_COMMA = r','
    t_layout_LPAREN = r'\('
    t_layout_RPAREN = r'\)'
    t_format_DBLVLINE = r'\|\|+'
    t_format_VLINE = r'\|'
    t_format_NUMBER = r'\d+(\.[0-9+])*i*'
    t_body_TAB = r'\t'
    t_body_EMPTYCELL = '\\\\\^'
    t_body_BLOCKSTART = r'T{'
    t_body_BLOCKEND = r'}T'
    t_body_TEXTBLOCK = r'([^}]|}(?!T))+'
    t_body_TEXT = r'[^\t\n]+'

    def t_body_NEWLINE(self, t):
        r'(\s*\n)+'
        self._line += t.value.count('\n')
        return t

    def t_layout_SEMICOLON(self, t):
        r';(\s*\n)+'
        self._current_state = ('body',)
        self._line += t.value.count('\n')
        t.value = t.value.strip()
        return t

    def t_format_FORMAT(self, t):
        r'(\b([Ll]|[Rr]|[Cc]|[Ss]|[Nn]|[Aa]|[Tt])|\^|_)'
        return t

    def t_format_DOT(self, t):
        r'\.(\s*\n)+'
        self._line += t.value.count('\n')
        self._current_state = ('format',)
        t.value = t.value.strip()
        return t

    def t_layout_TAB(self, t):
        r'\btab\s*\(\s*(?P<tab>[^)]+)\s*\)'
        tab = t.lexmatch.group('tab').strip()
        t.value = tab
        if len(tab) != 1:
            raise Exception('Invalid tab at line :' + t.lineno)
        self._set_tab(tab)
        return t

    def t_layout_LINESIZE(self, t):
        r'\blinesize\s*\(\s*(?P<linesize>[^)]+)\s*\)'
        t.value = t.lexmatch.group('linesize').strip()
        return t

    def t_format_ENDFMTLINE(self, t):
        r'(\n+|\s*,\s*)'
        return t

    def t_format_FONT(self, t):
        r'(f*[bBiI]|f*cw|f*CW|p(?P<fsize>[+-]?[0-9]+))'
        return t

    def t_format_NEWLINE(self, t):
        r'(\s*\n)+'
        self._line += len(t.value.replace(' ', ''))
        return t

if __name__ == '__main__':
    import unittest as ut
    lexer = TblLexer()

    class TestLayout(ut.TestCase):
        def _test_cases(self, samples, expected_tokens):
            for i, sample in enumerate(samples):
                lexer.input(sample)
                tok = lexer.token()
                while tok:
                    self.assertEqual(tok, expected_tokens[i].pop(0))
                    tok = lexer.token()

        def test_basic(self):
            samples = ['''allbox, center;
data1\tdata2''', '''data1\tdata2''', '''c l.
data1\tdata2''', '''box;
r l.
data1\tdata2''']
            expected_tokens = [[TblToken('ALLBOX', 'allbox'),
                 TblToken('COMMA', ','), TblToken('CENTER', 'center'),
                 TblToken('SEMICOLON', ';'), TblToken('TEXT', 'data1'),
                 TblToken('TEXT', 'data2')],
                [TblToken('TEXT', 'data1'), TblToken('TEXT', 'data2')],
                [TblToken('FORMAT', 'c'), TblToken('FORMAT', 'l'),
                 TblToken('DOT', '.'),
                 TblToken('TEXT', 'data1'), TblToken('TEXT', 'data2')],
                [TblToken('BOX', 'box'), TblToken('SEMICOLON', ';'),
                 TblToken('FORMAT', 'r'), TblToken('FORMAT', 'l'),
                 TblToken('DOT', '.'),
                 TblToken('TEXT', 'data1'), TblToken('TEXT', 'data2')]]

            self._test_cases(samples, expected_tokens)

        def test_tab(self):
            samples = ['''tab(@);
data1@data2''', '''tab(|);
r s s s.
one|two|three|four|five
''']
            expected_tokens = [[TblToken('TAB', '@'),
                 TblToken('SEMICOLON', ';'),
                 TblToken('TEXT', 'data1'), TblToken('TEXT', 'data2')],
                [TblToken('TAB', '|'), TblToken('SEMICOLON', ';'),
                 TblToken('FORMAT', 'r'), TblToken('FORMAT', 's'),
                 TblToken('FORMAT', 's'), TblToken('FORMAT', 's'),
                 TblToken('DOT', '.'),
                 TblToken('TEXT', 'one'), TblToken('TEXT', 'two'),
                 TblToken('TEXT', 'three'), TblToken('TEXT', 'four'),
                 TblToken('TEXT', 'five')]]
            self._test_cases(samples, expected_tokens)

        def test_empty(self):
            samples = ['''doublebox, tab(|);
c c
^ c.
data1|data2
\^|data4''']
            expected_tokens = [
                [TblToken('DOUBLEBOX', 'doublebox'), TblToken('COMMA', ','),
                 TblToken('TAB', '|'), TblToken('SEMICOLON', ';'),
                 TblToken('FORMAT', 'c'), TblToken('FORMAT', 'c'),
                 TblToken('ENDFMTLINE', '\n'),
                 TblToken('FORMAT', '^'), TblToken('FORMAT', 'c'),
                 TblToken('DOT', '.'),
                 TblToken('TEXT', 'data1'), TblToken('TEXT', 'data2'),
                 TblToken('EMPTYCELL', r'\^'), TblToken('TEXT', 'data4')]]
            self._test_cases(samples, expected_tokens)

        def test_textblock(self):
            samples = ['''data1\tT{this is
a block}T\tdata3
T{{}}T\t\^\t\^''']
            expected_tokens = [[TblToken('TEXT', 'data1'),
                TblToken('TEXT', '''this is
a block'''), TblToken('TEXT', 'data3'), TblToken('TEXT', '{}'),
                TblToken('EMPTYCELL', r'\^'), TblToken('EMPTYCELL', r'\^')]]
            self._test_cases(samples, expected_tokens)

        def test_fonts(self):
            samples = ['''rB ci rbI
rBp12 ci rbI.
data1\tdata2\tdata3''']
            expected_tokens = [[TblToken('FORMAT', 'r'), TblToken('FONT', 'B'),
                TblToken('FORMAT', 'c'), TblToken('FONT', 'i'),
                TblToken('FORMAT', 'r'), TblToken('FONT', 'b'),
                TblToken('FONT', 'I'), TblToken('ENDFMTLINE', '\n'),
                TblToken('FORMAT', 'r'), TblToken('FONT', 'B'),
                TblToken('FONT', 'p12'), TblToken('FORMAT', 'c'),
                TblToken('FONT', 'i'), TblToken('FORMAT', 'r'),
                TblToken('FONT', 'b'), TblToken('FONT', 'I'),
                TblToken('DOT', '.'), TblToken('TEXT', 'data1'),
                TblToken('TEXT', 'data2'), TblToken('TEXT', 'data3')]]
            self._test_cases(samples, expected_tokens)

    ut.main()
