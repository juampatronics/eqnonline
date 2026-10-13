# -*- coding: utf-8 -*-
"""
pyeqn a parser for the eqn language described in
  A system for Typesetting Mathematics
  Brian W. Kernighan and Lorinda L. Cherry
  CACM, March, 1975

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

from ply import lex
from ply import yacc
import re
from .utils import Translator, process_ast


class EqnException(Exception):
    'Trigger errors ought to wrong eqn syntax'
    pass

# Notice that here we do not use any token declaration of the form t_TOKEN =
# r'...'. This is because of the way PLY orders them. This leads to ambiguities
# when deciding what is just text and what not. Notice that eqn is very lax
# about it, and solving it through regexp would be harder and more error prone
# than just defining simple regexp while ensuring they are checked in a given
# order.  We need to ensure that t_TEXT will be checked last.


t_ANY_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


reserved_words = (
    'SUP', 'SUB', 'SUM', 'TO', 'LIM', 'TILDE', 'BAR', 'OVER', 'UNDER', 'HAT',
    'DOT', 'SIZE', 'PARTIAL', 'INT', 'PROD', 'UNION', 'HALF', 'PRIME', 'INTER',
    'APPROX', 'TIMES', 'DEL', 'GRAD', 'INF', 'CDOT', 'ABOVE', 'ROMAN', 'BOLD',
    'ITALIC', 'SQRT', 'UNDER', 'FROM', 'RPILE', 'CPILE', 'LPILE', 'PILE',
)

special_chars = [
    'pi', 'ALPHA', 'OMEGA', 'THETA', 'PSI', 'DELTA', 'GAMMA', 'EPSILON', 'ETA',
    'rho', 'mu', 'nu', 'lambda', 'alpha', 'beta', 'gamma', 'omega', 'tau',
    'theta', 'CHI', 'delta', 'kappa', 'eta', 'iota', 'omicron', 'psi', 'zeta',
    'LAMBDA', 'PHI', 'PI', 'SIGMA', 'UPSILON', 'XI', 'xi', 'upsilon', 'chi',
    'sigma', 'inf',
]


# Some tokens are used with different meanings, which leads to ambiguity in
# syntax. A way to solve this is to define distinguish tokens by its function.
states = (
    ('bracket', 'exclusive'),
)


def gen_reserved_dict(words_list, lowercase=False):
    return dict((k.lower() if lowercase else k, k) for k in words_list)


def define_specials(words, lowercase=False):
    if not lowercase:
        for s in words:
            exec('t_' + s + ' = r\'\\b' + s + '\\b\'')
    else:
        for s in words:
            exec('t_' + s + ' = r\'\\b' + s.lower() + '\\b\'')


reserved = gen_reserved_dict(reserved_words, True)
reserved.update(gen_reserved_dict(special_chars))

tokens = ['LCURLYB', 'RCURLYB', 'LBRACKET', 'RBRACKET', 'LEFT', 'RIGHT', 'TEXT',
          'SPACE']


def t_LCURLYB(t):
    r'\{'
    return t


def t_RCURLYB(t):
    r'\}'
    return t


# notice that curly braces have two meanings: one as grouping elements, and as a
# bracketing, graphical element.
def t_bracket_RBRACKET(t):
    r'[\]})>]'
    t.lexer.pop_state()
    return t


def t_bracket_LBRACKET(t):
    r'[[({<]'
    t.lexer.pop_state()
    return t


def t_SPACE(t):
    r'(~|\^)+'
    return t


math_symbols = ['GE', 'LE', 'EQ', 'NOTEQ', 'LARROW', 'DOTS',
                'RSHIFT', 'LSHIFT', 'PM']


def t_GE(t):
    r'>='
    return t


def t_LE(t):
    r'<='
    return t


def t_EQ(t):
    r'=='
    return t


def t_NOTEQ(t):
    r'!='
    return t


def t_LIM(t):
    r'->'
    return t


def t_LARROW(t):
    r'<-'
    return t


def t_DOTS(t):
    r'\.\.\.'
    return t


def t_RSHIFT(t):
    r'>>'
    return t


def t_LSHIFT(t):
    r'<<'
    return t


def t_PM(t):
    r'\+-'
    return t


def t_LEFT(t):
    r'\bleft\b'
    t.lexer.push_state('bracket')
    return t


def t_RIGHT(t):
    r'\bright\b'
    t.lexer.push_state('bracket')
    return t


def t_TEXT(t):
    r'("[^"]*"|[^\^~\s]+)'
    t.type = reserved.get(t.value, 'TEXT')
    return t


tokens = math_symbols + list(reserved.values()) + tokens


def t_ANY_error(t):
    print("Illegal character '%s' at line %d" % (t.value[0],
                                                 t.lexer.lineno))


tokenizer = lex.lex()


def print_tokens(lexer, data, logfile=None):
    import sys
    lexer.input(data)
    f = open(logfile, 'w') if logfile else sys.stdout
    while True:
        tok = lexer.token()
        if not tok:
            break
        f.write(tok.__str__())
        f.write("\n")

    if f is not sys.stdout:
        f.close()

# parser ============================================================


def eqnnode(ntype, *args):
    return (ntype, args)


def p_error(p):
    print("Error while parsing : ", p)


precedence = (
    ('left', 'FROM', 'TO'),
    ('left', 'OVER', 'SQRT'),
    ('right', 'HAT', 'TILDE', 'UNDER', 'ROMAN', 'ITALIC', 'BOLD', 'DOT', 'BAR'),
    ('right', 'SUP', 'SUB'),
)


def p_eqn(p):
    '''eqn : box
           | box eqn'''
    p[0] = p[1] + p[2] if len(p) > 2 else p[1]


def p_text(p):
    '''box : TEXT
           | SPACE'''
    p[0] = eqnnode('text', p[1])


def p_specialchar(p):
    '''box : alpha
           | beta
           | gamma
           | mu
           | pi
           | sigma
           | rho
           | xi
           | nu
           | kappa
           | lambda
           | upsilon
           | chi
           | delta
           | eta
           | iota
           | omicron
           | psi
           | tau
           | theta
           | zeta
           | DELTA
           | GAMMA
           | LAMBDA
           | OMEGA
           | PHI
           | PI
           | SIGMA
           | UPSILON
           | XI
           | PSI
           | omega
           | inf'''
    p[0] = eqnnode('special_char', p[1])


def p_bracketed(p):
    'box : LCURLYB eqn RCURLYB'
    p[0] = eqnnode('bracketed', *p[2])

# Unless braces are used, eqn performs the operations in the order given below


def p_decoration(p):
    '''box : box HAT
           | box BAR
           | box DOT
           | box UNDER
           | box TILDE'''
    p[0] = eqnnode(p[2], *p[1])


def p_txtfmt(p):
    '''box : ROMAN box
           | ITALIC box
           | BOLD box'''
    p[0] = eqnnode(p[1], *p[2])


# see UNIX Text Processing p.249
legal_sizes = [12, 14, 16, 18, 20, 22, 24, 28, 36]
default_size = 10
# one important reason to use closures or classes
current_size = default_size


def p_size(p):
    'box : SIZE TEXT box'
    if re.match('^[+-]?[0-9]+$', p[2]) == None:
        raise EqnException('Invalid size parameter: ' + p[2])
    # TODO: check correctness of text size
    p[0] = eqnnode(p[1], p[2], *p[3])


def p_supbox(p):
    'supbox : SUP box %prec SUP'
    p[0] = p[2]


def p_box_subsup(p):
    '''box : box SUB box supbox'''
    tmp = eqnnode(p[2], *(p[1] + p[3]))
    p[0] = eqnnode('sup', *(tmp + p[4]))


def p_subbox(p):
    'subbox : SUB box %prec SUB'
    p[0] = p[2]


def p_box_supsub(p):
    '''box : box SUP box subbox'''
    tmp = eqnnode(p[2], *(p[1] + p[3]))
    p[0] = eqnnode('sub', *(tmp + p[4]))


def p_box_script(p):
    '''box : box SUB box
           | box SUP box'''
    p[0] = eqnnode(p[2], *(p[1] + p[3]))


def p_box_mathops(p):
    '''box : SUM
           | PROD
           | INT
           | LIM'''
    p[0] = eqnnode('mathop', p[1])


def p_box_math(p):
    '''box : EQ
           | GE
           | LE
           | NOTEQ
           | LSHIFT
           | RSHIFT
           | PARTIAL
           | PM'''
    p[0] = eqnnode('mathop', p[1])


def p_box_fromto(p):
    '''box : box FROM box
           | box TO box'''
    p[0] = eqnnode(p[2], *(p[1] + p[3]))


def p_sqrt(p):
    '''box : SQRT box'''
    p[0] = eqnnode(p[1], *p[2])


def p_over(p):
    'box : box OVER box'
    p[0] = eqnnode(p[2], *(p[1] + p[3]))


def p_vectors(p):
    '''box : RPILE LCURLYB list RCURLYB
           | CPILE LCURLYB list RCURLYB
           | PILE  LCURLYB list RCURLYB
           | LPILE LCURLYB list RCURLYB'''
    p[0] = eqnnode(p[1], *p[3])


def p_list(p):
    '''list : eqn
            | list ABOVE eqn'''
    p[0] = eqnnode('above', *(p[1] + p[3])) if len(p) > 2 else p[1]


def p_brackets(p):
    '''box : LEFT LBRACKET eqn RIGHT RBRACKET
           | LEFT LBRACKET eqn'''
    if len(p) > 4:
        p[0] = eqnnode('brackets', *(eqnnode(p[1], p[2]) + p[3] +
                                     eqnnode(p[4], p[5])))
    else:
        p[0] = eqnnode('brackets', *(eqnnode(p[1], p[2]) + p[3]))


treebuilder = Translator(yacc.yacc(start='eqn'),
                         ['text', 'special_char', 'bracketed', 'hat', 'bar', 'dot',
                          'under', 'tilde', 'roman', 'italic', 'bold', 'size', 'sub',
                          'sup', 'sum', 'prod', 'int', 'from', 'to', 'sqrt', 'over',
                          'above', 'pile', 'rpile', 'lpile', 'cpile', 'brackets',
                          'mathop', 'left', 'right'])


