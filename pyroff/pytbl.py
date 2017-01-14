# -*- coding: utf-8 -*-
"""
pytbl.py A parser for the tbl language.

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

import inspect
import re
from functools import wraps
from .tbllexer import TblLexer
from .ast import TranslatorFactory, ASTNode, TokenNode


class ParserError(Exception):
    def __init__(self, msg, token):
        super(ParserError, self).__init__(msg)
        self.token = token
        self.msg = msg


class InvalidTokenError(ParserError):
    def __init__(self, token, expected=None):
        super(InvalidTokenError, self).__init__('Unexpected token', token)
        self.expected = expected

    def __str__(self):
        if not self.expected:
            return self.msg + ': got ' + self.token
        else:
            return self.msg + ': got ' + self.token + ', but expected : ' +\
                   self.expected


class TblParser(object):
    '''This tbl parser is a very simple state machine. For a given state, only
       some specific tokens are expected. This is coded in the dictionary
       self.states. For each state there is a corresponding method, named after
       the state and starting with the prefix 'p_' by convention, which is
       responsible for checking the validity of the next token, generating its
       tree node representation, and switching to the next state
       (for each state there is a token signaling its end, see man tbl).
    '''

    def __init__(self):
        symbols = inspect.getmembers(self)
        self.actions = dict((name[name.find('_') + 1:], f)
                            for name, f in symbols
                            if name.startswith('p_') and inspect.ismethod(f))

        self.states = {'layout': ['TAB', 'ALLBOX', 'EXPAND', 'CENTER',
                                   'LINESIZE', 'SEMICOLON', 'COMMA', 'BOX'],
                       'format': ['VLINE', 'DBLVLINE', 'FORMAT', 'FONT',
                                  'DOT', 'ENDFMTLINE'],
                       'data': ['TEXT', 'EMPTYLINE', 'EMPTYCELL',
                                'HLINE', 'DBLHLINE', 'NEWLINE']}
        self._reset()

    def _reset(self):
        self._current_state = ('layout', 'format', 'data')
        self._cell = []
        self._options = None
        self._ast = []
        self._tblrow = ASTNode('tblrow')
        self._nrow = 0
        self._ncol = 0
        # list keeping count of the number of cells beign expanded
        self._spancount = []
        self._spanrow = []

    def expected(self, t):
        'Checks whether the token is valid given the current state.'
        for state in self._current_state:
            if t.type in self.states[state]:
                return True
        return False

    def next_state(self, t):
        '''Returns the next state, given the current token. In the tbl
        language the options section for the table is optional. If present, it
        must be the first right after the .TS token. Thus, we need to wait for
        the next token to decide whether it is present or not.
        '''
        for s in self._current_state:
            if t.type in self.states[s]:
                return s
        return None

    def p_layout(self, t):
        if t.type == 'SEMICOLON':
            self._current_state = ('format',)
            if self._options is not None:
                self._ast.append(self._options)
            return
        if t.type == 'COMMA':
            return
        if self._options is None:
            self._options = ASTNode('tblformat',
                                    ASTNode('option', TokenNode(t.value)))
        else:
            self._options.add_children(ASTNode('option', TokenNode(t.value)))

    def p_format(self, t):
        if t.type == 'FORMAT':
            # s means expanding options defined in prev cell.
            if t.value.lower() == 's':
                if len(self._cell) == 0:
                    raise InvalidTokenError(t)
                if not self._cell[-1].has_key('colspan'):
                    self._cell[-1]['colspan'] = 2
                else:
                    self._cell[-1]['colspan'] += 1
            else:
                self._cell.append(ASTNode('cellfmt', TokenNode(t.value)))
            return

        if t.type == 'FONT':
            # we decided to add font as metadata because in troff the font can
            # only be specified after the column key letter (l,c,r)
            t.value = t.value.lower()
            attr = self._cell[-1].get('font', dict())
            if 'b' in t.value:
                attr['bold'] = True
            if 'i' in t.value:
                attr['italic'] = True
            if 'p' in t.value:
                attr['size'] = re.match('.*p([+-]?[0-9]+)', t.value).group(1)
            self._cell[-1]['font'] = attr

        if t.type == 'DOT' or t.type == 'ENDFMTLINE':
            if len(self._cell) > 0:
                self._ast.append(ASTNode('cellfmtline', self._cell))
                self._cell = []
        if t.type == 'DOT':
            self._current_state = ('data',)

    def _update_span_attr(self, col):
        nspan = self._spancount[col]
        if nspan == 0:
            return
        self._ast[-nspan-1]._children[col]['span'] = nspan + 1
        self._spancount[col] = 0

    def _add_row(self):
        'adds the current row to the AST'
        if not self._tblrow.is_empty():
            self._ast.append(self._tblrow)
            self._nrow += 1
            self._ncol = 0

    def p_data(self, t):
        if t.type == 'END':
            self._current_state = ('start',)
            # check for remaining spanning cells
            for col in range(len(self._spancount)):
                self._update_span_attr(col)
            return

        if t.type == 'NEWLINE':
            # we need to skip (multiple) newlines before next data
            self._add_row()
            self._tblrow = ASTNode('tblrow')
            return

        if t.type == 'EMPTYCELL':
            # using ^ to span cells refers to prev non-empty cell
            if not self._tblrow.is_empty() and self._nrow == 0:
                raise InvalidTokenError(t)
            t.value = ''
            self._spancount[self._ncol] += 1
            self._ncol += 1
            self._tblrow.add_children(ASTNode('cell', TokenNode(t.value)))
            return

        self._tblrow.add_children(ASTNode('cell', TokenNode(t.value)))
        # expand the self._spancount array to max # of columns
        if self._ncol >= len(self._spancount):
            self._spancount += [0 for n in
                                range(self._ncol - len(self._spancount) + 1)]
        self._update_span_attr(self._ncol)
        self._ncol += 1

    def parse(self, data, debug=False):
        lexer = TblLexer(debug)
        lexer.input(data)
        self._current_state = ('layout', 'format', 'data')
        while True:
            tok = lexer.token()
            if not tok or not self.expected(tok):
                break
            state = self.next_state(tok)
            if state is None:
                raise InvalidTokenError(tok)
            self.actions[state](tok)

        # add last row
        self._add_row()

        for col in range(len(self._spancount)):
            self._update_span_attr(col)
        ast = ASTNode('tbl', self._ast)
        self._reset()
        return ast


class TblTranslator(TranslatorFactory):
    expected = ['tblformat', 'option', 'cellfmt', 'cellfmtline',
                'tblrow', 'cell', 'tbl']

    def __init__(self):
        super(TblTranslator, self).__init__(TblParser(), 'tbl_')


if __name__ == "__main__":
    import unittest as ut

    class BasicTests(ut.TestCase):
        def setUp(self):
            self.parser = TblParser()

        def _test_cases(self, expressions, expected):
            for expr, should in zip(expressions, expected):
                ast = self.parser.parse(expr)
                self.assertEqual(should, ast)

        def test_tables(self):
            expressions = ['''tab (@);
                c l.
                1@User Console
                2@Monochromatic graphics terminal
                3@Touch screen
                4@High resolution display''', '''center,box,tab(%);
                c l.
                1%User Console
                2%Monochromatic graphics terminal
                3%Touch screen
                4%High resolution display''', '''tab(|);
                c l
                r r.
                1|User Console
                2|Monochromatic graphics terminal
                3|Touch screen
                4|High resolution display''', '''tab(|);
                c _
                r r.
                vertically centered|User Console
                \^|Monochromatic graphics terminal
                \^|Touch screen
                \^|High resolution display
                =''']

            expected = [
                ASTNode('tbl',
                        [ASTNode('tblformat',
                                 ASTNode('option', [TokenNode('@')])),
                         ASTNode('cellfmtline',
                                 [ASTNode('cellfmt', TokenNode('c')),
                                  ASTNode('cellfmt', TokenNode('l'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('1')),
                                  ASTNode('cell', TokenNode('User Console'))]),
                         ASTNode('tblrow', [ASTNode('cell', TokenNode('2')),
                                            ASTNode('cell',
                                                    TokenNode('Monochromatic' +
                                                              ' graphics ' +
                                                              'terminal'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('3')),
                                  ASTNode('cell', TokenNode('Touch screen'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('4')),
                                  ASTNode('cell', TokenNode(
                                      'High resolution display'))])]),

                ASTNode('tbl',
                        [ASTNode('tblformat',
                                 [ASTNode('option', [TokenNode('center')]),
                                  ASTNode('option', [TokenNode('box')]),
                                  ASTNode('option', [TokenNode('%')])]),
                         ASTNode('cellfmtline',
                                 [ASTNode('cellfmt', TokenNode('c')),
                                  ASTNode('cellfmt', TokenNode('l'))]),
                         ASTNode('tblrow', [ASTNode('cell', TokenNode('1')),
                                            ASTNode('cell', TokenNode(
                                                'User Console'))]),
                         ASTNode('tblrow', [ASTNode('cell', TokenNode('2')),
                                            ASTNode('cell', TokenNode(
                                                'Monochromatic graphics ' +
                                                'terminal'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('3')),
                                  ASTNode('cell', TokenNode('Touch screen'))]),
                         ASTNode('tblrow', [ASTNode('cell', TokenNode('4')),
                                            ASTNode('cell', TokenNode(
                                                'High resolution display'))])]),

                ASTNode('tbl',
                        [ASTNode('tblformat',
                                 ASTNode('option', [TokenNode('|')])),
                         ASTNode('cellfmtline',
                                 [ASTNode('cellfmt', TokenNode('c')),
                                  ASTNode('cellfmt', TokenNode('l'))]),
                         ASTNode('cellfmtline',
                                 [ASTNode('cellfmt', TokenNode('r')),
                                  ASTNode('cellfmt', TokenNode('r'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('1')),
                                  ASTNode('cell', TokenNode('User Console'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('2')),
                                  ASTNode('cell', TokenNode(
                                      'Monochromatic graphics terminal'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('3')),
                                  ASTNode('cell', TokenNode('Touch screen'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('4')),
                                  ASTNode('cell', TokenNode(
                                      'High resolution display'))])]),

                ASTNode('tbl',
                        [ASTNode('tblformat',
                                 ASTNode('option', [TokenNode('|')])),
                         ASTNode('cellfmtline',
                                 [ASTNode('cellfmt', TokenNode('c')),
                                  ASTNode('cellfmt', TokenNode('_'))]),
                         ASTNode('cellfmtline',
                                 [ASTNode('cellfmt', TokenNode('r')),
                                  ASTNode('cellfmt', TokenNode('r'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode(
                                     'vertically centered')),
                                  ASTNode('cell', TokenNode('User Console'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('')),
                                  ASTNode('cell', TokenNode(
                                      'Monochromatic graphics terminal'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('')),
                                  ASTNode('cell', TokenNode('Touch screen'))]),
                         ASTNode('tblrow',
                                 [ASTNode('cell', TokenNode('')),
                                  ASTNode('cell', TokenNode(
                                      'High resolution display'))]),
                         ASTNode('tblrow', ASTNode('cell', TokenNode('=')))])
            ]

            self._test_cases(expressions, expected)

        def test_span(self):
            'check wether cells are properly spanned over rows'

            expressions = ['''tab(|);
                c _
                r r.
                vertically centered|User Console
                \^|Monochromatic graphics terminal
                stop|Touch screen''', '''tab(|);
                c c
                l r.
                vertically centered|User Console
                \^|Monochromatic graphics terminal
                \^|Touch screen
                \^|High resolution display''']

            expected = [2, 4]

            for expr, span in zip(expressions, expected):
                ast = self.parser.parse(expr)
                self.assertEqual(ast._children[3]._children[0]['span'], span)

        def test_colspan(self):
            expressions = ['''tab(|);
                r s s s.
                one|two|three|four|five
                1|2|3|4|5
                1|2|3|4|5''', '''tab(|);
                r c s r.
                vertically centered|User Console
                Monochromatic graphics terminal
                Touch screen
                High resolution display''']

            expected = [(0, 4), (1, 2)]

            for expr, span in zip(expressions, expected):
                ast = self.parser.parse(expr)
                self.assertEqual(span[1],
                                 ast._children[1]._children[span[0]]['colspan'])

        def test_font(self):
            expressions = ['''tab(|);
                rB ci rbI
                rBp12 ci rbI.
                one|two|three|four|five
                1|2|3|4|5
                1|2|3|4|5''']

            expected = [(1, 0, {'bold': True}), (1, 1, {'italic': True}),
                        (1, 2, {'italic': True, 'bold': True}),
                        (2, 0, {'bold': True, 'size': '12'}),
                        (2, 1, {'italic': True}),
                        (2, 2, {'italic': True, 'bold': True})]

            for expr, values in zip(expressions, expected):
                ast = self.parser.parse(expr)
                self.assertEqual(
                    values[2],
                    ast._children[values[0]]._children[values[1]]['font'])

    ut.main()
