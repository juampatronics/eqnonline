# -*- coding: utf-8 -*-
"""
PIC - A Language for Typesetting Graphics
  Brian W. Kernighan
  Software Practice Experience (12): 1–20, 1982

Copyright (C) 2020
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

from ply import lex
from ply import yacc
import re
import inspect


class PicException(Exception):
    'Trigger errors ought to wrong eqn syntax'
    pass


primitives = ['CIRCLE', 'ELLIPSE', 'LINE', 'ARC', 'ARROW', 'BOX', 'SPLINE']
commands = ['ABOVE', 'BELOW', 'MOVE',
            'UP', 'DOWN', 'RIGHT', 'LEFT', 'THEN', 'SAME', 'END', 'TOP', 'BOTTOM']
references = ['LAST', 'OF', 'FROM', 'TO']
attributes = ['DASHED', 'DOTTED']
default_radius = 0.25  # inches


def gen_reserved_dict(words_list, lowercase=False):
    return dict((k.lower() if lowercase else k, k) for k in words_list)


reserved = gen_reserved_dict(commands, True)
reserved.update(gen_reserved_dict(primitives, True))
reserved.update(gen_reserved_dict(references, True))
reserved.update(gen_reserved_dict(attributes, True))

tokens = ['WIDTH', 'HEIGHT', 'RADIUS', 'DIAMETER', 'NUMBER', 'LABEL', 'CMDEND',
          'FIRST', 'SECOND'] + list(reserved.values())

def t_RESERVED(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_WIDTH(t):
    r'(width|wid)'
    # better return canonical form: 'width'
    return t


def t_HEIGHT(t):
    r'(height|ht)'
    # better return canonical form
    return t


def t_RADIUS(t):
    r'(radius|rad)'
    return t


def t_DIAMETER(t):
    r'(diameter|diam)'
    return t


def t_NUMBER(t):
    r'[0-9]*\.?[0-9]+'
    t.value = float(t.value)
    return t


def t_LABEL(t):
    r'"[^"]+"'
    return t


def t_CMDEND(t):
    r';'
    return t


def t_FIRST(t):
    r'(first|1st)'
    return t


def t_SECOND(t):
    r'(second|2nd)'
    return t


def t_ANY_error(t):
    print("Illegal character '%s' at line %d" % (t.value[0],
                                                 t.lexer.lineno))


tokenizer = lex.lex()

# parser ============================================================

def picnode(ntype, *args):
    return (ntype, args)


def p_error(p):
    print("Error while parsing : ", p)


def p_pic(p):
    '''pic : direction pic
           | primitive pic
           |'''
    p[0] = p[1] + p[2]


def p_direction(p):
    '''direction : DOWN
                 | UP
                 | RIGHT
                 | LEFT'''
    p[0] = eqnnode('direction', p[1])


def p_primitive(p):
    '''primitive : circle
                 | line'''
    p[0] = eqnnode('primitive', p[1])


def p_circle(p):
    '''circle : CIRCLE cattr
              | CIRCLE'''
    p[0] = eqnnode('circle', *p[2]) if len(p) > 2 else eqnnode('cicle', None)


def p_cattr(p):
    '''cattr : RADIUS NUMBER
             | LABEL'''
    p[0] = eqnnode('cattr', *p[1:])


def p_line(p):
    '''line : LINE'''
    p[0] = eqnnode('line', None)


if __name__ == "__main__":
    import unittest as ut

    class TestLexer(ut.TestCase):
        def setUp(self):
            self.pixer = lex.lex()

        def run_tests(self, cases, expected, tag):
            for c, e in zip(cases, expected):
                self.pixer.input(c)
                token = next(self.pixer)
                self.assertEqual(token.value, e)
                self.assertEqual(token.type, tag)

        def test_number(self):
            cases = ['.1', '0.35', '545', '234.24545']
            expected = [float(n) for n in cases]
            self.run_tests(cases, expected, 'NUMBER')

        def test_label(self):
            cases = ['"valid"',
                     '"valid23$%&/(fe"', '" wgökjwg ojwgog    jgnpgo"']
            self.run_tests(cases, cases, 'LABEL')

            for wrong in ['dwfewgf wdg', '"grg']:
                with self.assertRaises(lex.LexError):
                    self.pixer.input(wrong)
                    next(self.pixer)

        def test_reserved(self):
            for txt in reserved:
                self.pixer.input(txt)
                token = next(self.pixer)
                self.assertEqual(token.value, txt)
                self.assertEqual(token.type, txt.upper())

        def test_fullcommands(self):
            cases = ['''ellipse
move down 1.25
circle radius .35
move left 1i from left of last circle; box
arrow from lower left of las ellipse to top of 1st box''']
            for txt in cases:
                self.pixer.input(txt)
                [t for t in self.pixer]

    class TestParser(ut.TestCase):
        def setUp(self):
            self._parser = yacc.yacc(start='pic')

        def test_buildgrammar(self):
            pass

        def test_circle(self):
            examples = ['circle', 'down ; circle', 'circle radius 0.5']
            expected = []

        def _test_badgrammar(self):
            examples = ['circle 0.5']
            for s in examples:
                with self.assertRaises(yacc.YaccError):
                    self._parser.parse(s)

    ut.main()
