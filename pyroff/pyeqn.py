# -*- coding: utf-8 -*-
"""
pyeqn a parser for the eqn language described in
  A system for Typesetting Mathematics
  Brian W. Kernighan and Lorinda L. Cherry
  CACM, March, 1975

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

from ply import lex
from ply import yacc
from functools import wraps
import re
import inspect

# Notice that here we do not use any token declaration of the form t_TOKEN =
# r'...'. This is because of the way PLY orders them. This leads to ambiguities
# when deciding what is just text and what not. Notice that eqn is very lax
# about it, and solving it through regexp would be harder and more error prone
# than just defining simple regexp while ensuring they are checked in a given
# order.  We need to ensure that t_TEXT will be checked last.

t_ignore = ' \t\^~'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

reserved_words = (
    'SUP', 'SUB', 'SUM', 'TO', 'LIM', 'TILDE', 'BAR', 'OVER', 'UNDER', 'HAT',
    'DOT', 'SIZE', 'PARTIAL', 'INT', 'PROD', 'UNION', 'HALF', 'PRIME', 'INTER',
    'APPROX', 'TIMES', 'DEL', 'GRAD', 'INF', 'CDOT', 'ABOVE', 'ROMAN', 'BOLD',
    'ITALIC', 'SQRT', 'UNDER', 'FROM', 'RPILE', 'CPILE', 'LPILE', 'PILE',
    'LEFT', 'RIGHT',
    )

special_chars = [
    'pi', 'ALPHA', 'OMEGA', 'THETA', 'PSI', 'DELTA', 'GAMMA', 'EPSILON', 'ETA',
    'rho', 'mu', 'nu', 'lambda', 'alpha', 'beta', 'gamma', 'omega', 'tau',
    'theta', 'CHI', 'delta', 'kappa', 'eta', 'iota', 'omicron', 'psi', 'zeta',
    'LAMBDA', 'PHI', 'PI', 'SIGMA', 'UPSILON', 'XI', 'xi', 'upsilon', 'chi',
    'sigma',
    ]


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

# tokens = ['LCURLYB', 'RCURLYB', 'SPACE', 'TEXT']
tokens = ['LCURLYB', 'RCURLYB', 'TEXT']


def t_LCURLYB(t):
    r'\{'
    return t


def t_RCURLYB(t):
    r'\}'
    return t


def t_SPACE(t):
    r'(~|\^)+'
    return t


math_symbols = ['GE', 'LE', 'EQ', 'NOTEQ', 'RARROW', 'LARROW', 'DOTS',
                'RSHIFT', 'LSHIFT']


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


def t_RARROW(t):
    r'->'
    return t


def t_LARROW(t):
    r'<-'
    return t


def t_DOTS(t):
    '\.\.\.'
    return t


def t_RSHIFT(t):
    r'>>'
    return t


def t_LSHIFT(t):
    r'<<'
    return t


def t_TEXT(t):
    r'("[^"]*"|[^\^~\s]+)'
    t.type = reserved.get(t.value, 'TEXT')
    return t

tokens += math_symbols + list(reserved.values())


def t_error(t):
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


def trace_rule(rule):
    @wraps(rule)
    def wrapper(p):
        print(rule.__name__ + ' >> ', p[1:])
        rule(p)
        print(rule.__name__ + ' << ', p[0])
    return wrapper


def p_error(p):
    print("Error while parsing : ", p)


precedence = (
    ('left', 'FROM', 'TO'),
    ('left', 'OVER', 'SQRT'),
    ('right', 'HAT', 'TILDE', 'UNDER', 'ROMAN', 'ITALIC', 'BOLD', 'DOT', 'BAR'),
    ('right', 'SUP', 'SUB'),
    )


# @trace_rule
def p_eqn(p):
    '''eqn : box
           | box eqn'''
    p[0] = p[1] + p[2] if len(p) > 2 else p[1]


# @trace_rule
def p_box_texr(p):
    'box : TEXT'
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
           | omega'''
    p[0] = eqnnode('special_char', p[1])


# @trace_rule
def p_bracketed(p):
    'box : LCURLYB eqn RCURLYB'
    p[0] = eqnnode('bracketed', *p[2])

# Unless braces are used, eqn performs the operations in the order given below


# @trace_rule
def p_decoration(p):
    '''box : box HAT
           | box BAR
           | box DOT
           | box UNDER
           | box TILDE'''
    p[0] = eqnnode(p[2], *p[1])


# @trace_rule
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


# @trace_rule
def p_size(p):
    'box : SIZE TEXT box'
    if re.match('^[+-]?[0-9]+$', p[2]) == None:
        raise Exception('Invalid size parameter: ' + p[2])
    # TODO: check correctness of text size
    p[0] = eqnnode(p[1], p[2], *p[3])


# @trace_rule
def p_supbox(p):
    'supbox : SUP box %prec SUP'
    p[0] = p[2]


# @trace_rule
def p_box_subsup(p):
    '''box : box SUB box supbox'''
    tmp = eqnnode(p[2], *(p[1] + p[3]))
    p[0] = eqnnode('sup', *(tmp + p[4]))


# @trace_rule
def p_subbox(p):
    'subbox : SUB box %prec SUB'
    p[0] = p[2]


# @trace_rule
def p_box_supsub(p):
    '''box : box SUP box subbox'''
    tmp = eqnnode(p[2], *(p[1] + p[3]))
    p[0] = eqnnode('sub', *(tmp + p[4]))


# @trace_rule
def p_box_script(p):
    '''box : box SUB box
           | box SUP box'''
    p[0] = eqnnode(p[2], *(p[1] + p[3]))


# @trace_rule
def p_box_mathops(p):
    '''box : SUM
           | PROD
           | INT
           | LIM'''
    p[0] = eqnnode('mathop', p[1])


# @trace_rule
def p_box_math(p):
    '''box : EQ
           | GE
           | LE
           | NOTEQ
           | LSHIFT
           | RSHIFT
           | PARTIAL'''
    p[0] = eqnnode('mathop', p[1])


# @trace_rule
def p_box_fromto(p):
    '''box : box FROM box
           | box TO box'''
    p[0] = eqnnode(p[2], *(p[1] + p[3]))


# @trace_rule
def p_sqrt(p):
    '''box : SQRT box'''
    p[0] = eqnnode(p[1], *p[2])


# @trace_rule
def p_over(p):
    'box : box OVER box'
    p[0] = eqnnode(p[2], *(p[1] + p[3]))


# @trace_rule
def p_vectors(p):
    '''box : RPILE LCURLYB list RCURLYB
           | CPILE LCURLYB list RCURLYB
           | PILE  LCURLYB list RCURLYB
           | LPILE LCURLYB list RCURLYB'''
    p[0] = eqnnode(p[1], *p[3])


# @trace_rule
def p_list(p):
    '''list : eqn
            | list ABOVE eqn'''
    p[0] = eqnnode('above', *(p[1] + p[3])) if len(p) > 2 else p[1]


# @trace_rule
def p_brackets(p):
    '''box : LEFT TEXT eqn RIGHT TEXT
           | LEFT TEXT eqn'''
    if len(p) > 4:
        p[0] = eqnnode('brackets', *((p[2],) + p[3] + (p[5],)))
    else:
        p[0] = eqnnode('brackets', *((p[2],) + p[3]))

# converter =========================================================


def pairwise(iterable):
    'iterates over pairs (a0, a1), (a2, a3), ...'
    a = iter(iterable)
    return zip(a, a)


def process_ast(tree, callbacks):
    if tree is None or callbacks is None:
        return None
    nodes = []
    for nodetype, args in pairwise(tree):
        transformed = process_ast(args, callbacks) if len(args) > 1 \
                                                   else args[0]
        if nodetype not in callbacks:
            raise Exception('Undefined callback: ' + nodetype)
        if type(transformed) == tuple:
            nodes.append(callbacks[nodetype](*transformed))
        else:
            nodes.append(callbacks[nodetype](transformed))
    return tuple(nodes)


class EqnTranslator(object):
    expected = ['text', 'special_char', 'bracketed', 'hat', 'bar', 'dot',
                'under', 'tilde', 'roman', 'italic', 'bold', 'size', 'sub',
                'sup', 'sum', 'prod', 'int', 'from', 'to', 'sqrt', 'over',
                'above', 'pile', 'rpile', 'lpile', 'cpile', 'brackets',
                'mathop']

    @classmethod
    def custom(self, module, prefix=None):
        class Converter(object):
            def __init__(self, pymodule, prefix=None):
                self._parser = yacc.yacc(start='eqn',
                                         debug=False, optimize=True)
                members = inspect.getmembers(pymodule)
                if prefix is not None:
                    self._callbacks = dict((re.sub(prefix, '', name), handler)
                        for name, handler in members
                        if re.sub(prefix, '', name) in EqnTranslator.expected)
                else:
                    self._callbacks = dict((name, handler)
                                           for name, handler in members
                                           if name in EqnTranslator.expected)

            def translate(self, s):
                t = self._parser.parse(s)
                return ''.join(process_ast(t, self._callbacks))

            def translate_file(self, filename):
                with open(filename, 'r') as f:
                    return translate(self.parse(f.readlines()))

        return Converter(module, prefix)


if __name__ == "__main__":
    import unittest as ut
    import cProfile
    debug_mode = True

    # callbacks used to generate back the input, in order to perform some tests
    def binop(name):
        def func(*args):
            return args[0] + ' ' + name + ' ' + args[1]
        func.__doc__ = name
        return func

    def bracketed(*args):
        return '{ ' + ' '.join(args) + ' }'

    def text_size(*args):
        pass

    redocallbacks = {
        'text': lambda t: t,
        'over': binop('over'),
        'sub': binop('sub'),
        'sup': binop('sup'),
        'above': binop('above'),
        'bracketed': bracketed,
        'special_char': lambda c: c,
        'size': text_size,
        }

    def print_node(*args):
        for a in args:
            print(a)

    class TestExpressions(ut.TestCase):
        _parser = yacc.yacc(start='eqn', debug=debug_mode)
        def setUp(self):
            pass

        def _runtests(self, examples, expected):
            for i, s in enumerate(examples):
                t = self._parser.parse(s)
                self.assertEqual(t, expected[i])

        def test_subscripts(self):
            examples = ['x sup y+z', 'x sup y +z', '"" sup 2 He',
                        'x sub i sup j', 'y sub 1=x sup 2+^1']
            expected = [('sup', ('text', ('x',), 'text', ('y+z',))),
                        ('sup', ('text', ('x',), 'text', ('y',)),
                         'text', ('+z',)),
                        ('sup', ('text', ('""',), 'text', ('2',)),
                         'text', ('He',)),
                        ('sup', ('sub', ('text', ('x',), 'text', ('i',)),
                            'text', ('j',))),
                        ('sup', ('sub', ('text', ('y',), 'text', ('1=x',)),
                            'text', ('2+',)), 'text', ('1',))]

            self._runtests(examples, expected)

        def test_fractions(self):
            examples = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+^1 }']
            expected = [('over', ('text', ('x',), 'text', ('y+z',))),
                        ('over', ('text', ('x',), 'text', ('y',)),
                         'text', ('+z',)),
                        ('over', ('text', ('y',),
                                  'bracketed', ('sup', ('text', ('1=x',),
                                                        'text', ('2+',)),
                                                'text', ('1',))))]
            self._runtests(examples, expected)

        def test_decoration(self):
            examples = ['x dot under + x hat + y tilde = z+Z bar']
            expected = [('under', ('dot', ('text', ('x',))),
                         'text', ('+',), 'hat', ('text', ('x',)),
                         'text', ('+',), 'tilde', ('text', ('y',)),
                         'text', ('=',), 'bar', ('text', ('z+Z',)))]
            self._runtests(examples, expected)

        def test_specialcharacters(self):
            examples = ['alpha = 1', 'alpha=1', 'f( theta , xi , omega )',
                        'f(mu, sigma )']
            expected = [('special_char', ('alpha',), 'text', ('=',),
                         'text', ('1',)),
                        ('text', ('alpha=1',)),
                        ('text', ('f(',), 'special_char', ('theta',),
                         'text', (',',), 'special_char', ('xi',),
                         'text', (',',), 'special_char', ('omega',),
                         'text', (')',)),
                        ('text', ('f(mu,',), 'special_char', ('sigma',),
                         'text', (')',))]
            self._runtests(examples, expected)

        def test_mathops(self):
            examples = ['sum from { i=0 } to N-1 x sub i',
                        'x == y < z > u']
            expected = [('to', ('from', ('mathop', ('sum',),
                'bracketed', ('text', ('i=0',))), 'text', ('N-1',)),
                'sub', ('text', ('x',), 'text', ('i',))),
                ('text', ('x',), 'mathop', ('==',), 'text', ('y',),
                    'text', ('<',), 'text', ('z',), 'text', ('>',),
                    'text', ('u',))]
            self._runtests(examples, expected)

        def test_size(self):
            examples = ['size +3 x =y', 'size 8 { A + B }']
            expected = [('size', ('+3', 'text', ('x',)), 'text', ('=y',)),
                        ('size', ('8', 'bracketed', ('text', ('A',),
                                                     'text', ('+',),
                                                     'text', ('B',))))]
            self._runtests(examples, expected)

        def test_piles(self):
            examples = ['rpile { 0 above 2x above 1 }']
            expected = [('rpile', ('above',
                                   ('above', ('text', ('0',), 'text', ('2x',)),
                                    'text', ('1',))))]
            self._runtests(examples, expected)

        def test_brackets(self):
            examples = ['left [ rpile { 0 above 2x above 1 }',
                        'left [ rpile { 0 above 2x above 1 } right ]']
            expected = [('brackets', ('[', 'rpile',
                                      ('above', ('above', ('text', ('0',),
                                                           'text', ('2x',)),
                                                 'text', ('1',))))),
                        ('brackets', ('[', 'rpile',
                                      ('above',
                                       ('above', ('text', ('0',),
                                                  'text', ('2x',)),
                                        'text', ('1',))),
                                      ']'))]
            self._runtests(examples, expected)

    class TestConversion(ut.TestCase):
        def setUp(self):
            self._parser = yacc.yacc(start='eqn', debug=debug_mode)

        def test_fractions(self):
            examples = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+^1 }']
            expected = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+ 1 }']
            for i, s in enumerate(examples):
                t = self._parser.parse(s)
                result = ' '.join(process_ast(t, redocallbacks))
                self.assertEqual(expected[i], result)

    eqnparser = yacc.yacc(start='eqn', debug=False, optimize=True)

    def eqn(s): return eqnparser.parse(s)

    class TestProfiler(ut.TestCase):
        def test_profile_parser(self):
            if debug_mode:
                return
            examples = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+^1 }']
            for s in examples:
                cProfile.run('eqn(\'' + s + '\')')

    suite = ut.TestSuite()
    suite.addTest(ut.makeSuite(TestExpressions))
    suite.addTest(ut.makeSuite(TestConversion))
    suite.addTest(ut.makeSuite(TestProfiler))
    runner = ut.TextTestRunner()
    runner.run(suite)
