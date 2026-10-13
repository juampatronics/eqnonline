import unittest as ut
import cProfile

# PLY builds the parser out of the grammar definitions that are visible in
# the calling module's namespace, so re-export pyroff.pyeqn here.
from pyroff.pyeqn import *  # noqa: F401,F403
from pyroff.pyeqn import yacc
from pyroff.utils import process_ast

debug_mode = False

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
    # moved this out of setUp to speed up tests
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
                             'text', ('2+',)), 'text', ('^',),
                     'text', ('1',))]

        self._runtests(examples, expected)

    def test_fractions(self):
        examples = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+^1 }']
        expected = [('over', ('text', ('x',), 'text', ('y+z',))),
                    ('over', ('text', ('x',), 'text', ('y',)),
                     'text', ('+z',)),
                    ('over', ('text', ('y',),
                              'bracketed', ('sup', ('text', ('1=x',),
                                                    'text', ('2+',)),
                                            'text', ('^',),
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
                    'x == y < z > u',
                    'x +- y']
        expected = [('to', ('from', ('mathop', ('sum',),
                                     'bracketed', ('text', ('i=0',))),
                            'text', ('N-1',)),
                     'sub', ('text', ('x',), 'text', ('i',))),
                    ('text', ('x',), 'mathop', ('==',), 'text', ('y',),
                     'text', ('<',), 'text', ('z',), 'text', ('>',),
                     'text', ('u',)),
                    ('text', ('x',), 'mathop', ('+-',), 'text', ('y',))]
        self._runtests(examples, expected)

    def test_size(self):
        examples = ['size +3 x =y', 'size 8 { A + B }']
        expected = [('size', ('+3', 'text', ('x',)), 'text', ('=y',)),
                    ('size', ('8', 'bracketed', ('text', ('A',),
                                                 'text', ('+',),
                                                 'text', ('B',))))]
        self._runtests(examples, expected)

    def test_piles(self):
        examples = ['rpile { 0 above 2x above 1 }',
                    'left [ rpile { 0 above 2x above 1 }',
                    'left [ rpile { 0 above 2x above 1 } right ]']
        expected = [('rpile', ('above',
                               ('above', ('text', ('0',), 'text', ('2x',)),
                                'text', ('1',)))),
                    ('brackets', ('left', ('[',), 'rpile',
                                  ('above', ('above', ('text', ('0',),
                                                       'text', ('2x',)),
                                             'text', ('1',))))),
                    ('brackets', ('left', ('[',), 'rpile',
                                  ('above',
                                   ('above', ('text', ('0',),
                                              'text', ('2x',)),
                                    'text', ('1',))),
                                  'right', (']',)))
                    ]
        self._runtests(examples, expected)

    def test_brackets(self):
        examples = ['left ( x sup 2 over 2 right )',
                    'left { x sup 2 over 2 right }',
                    'left [ x sup 2 over 2 right ]',
                    'left < x sup 2 over 2 right >']
        expected = [
            ('brackets', ('left', ('(',),
                          'over', ('sup', ('text', ('x',), 'text', ('2',)),
                                   'text', ('2',)),
                          'right', (')',))),
            ('brackets', ('left', ('{',),
                          'over', ('sup', ('text', ('x',), 'text', ('2',)),
                                   'text', ('2',)),
                          'right', ('}',))),
            ('brackets', ('left', ('[',),
                          'over', ('sup', ('text', ('x',), 'text', ('2',)),
                                   'text', ('2',)),
                          'right', (']',))),
            ('brackets', ('left', ('<',),
                          'over', ('sup', ('text', ('x',), 'text', ('2',)),
                                   'text', ('2',)),
                          'right', ('>',)))
        ]

        self._runtests(examples, expected)

    def test_symbols(self):
        examples = ['x -> y', 'x -> inf']
        expected = [('text', ('x',), 'mathop', ('->',), 'text', ('y',)),
                    ('text', ('x',), 'mathop', ('->',),
                     'special_char', ('inf',))]
        self._runtests(examples, expected)

    def test_spaces(self):
        examples = ['x sup 2^+~1', 'x sup 2+~1']
        expected = [('sup', ('text', ('x',), 'text', ('2',)),
                     'text', ('^',), 'text', ('+',), 'text', ('~',),
                     'text', ('1',)),
                    ('sup', ('text', ('x',), 'text', ('2+',)),
                     'text', ('~',), 'text', ('1',))]
        self._runtests(examples, expected)


class TestConversion(ut.TestCase):
    def setUp(self):
        self._parser = yacc.yacc(start='eqn', debug=debug_mode)

    def test_fractions(self):
        examples = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+^1 }']
        expected = ['x over y+z', 'x over y +z',
                    'y over { 1=x sup 2+ ^ 1 }']
        for i, s in enumerate(examples):
            t = self._parser.parse(s)
            result = ' '.join(process_ast(t, redocallbacks))
            self.assertEqual(expected[i], result)


eqnparser = yacc.yacc(start='eqn', debug=False, optimize=True)


def eqn(s): return eqnparser.parse(s)

# cProfile.run() execs the statement in __main__'s namespace, so expose eqn there
import __main__
__main__.eqn = eqn


class TestProfiler(ut.TestCase):
    def test_profile_parser(self):
        if debug_mode:
            return

        examples = ['x over y+z', 'x over y +z', 'y over { 1=x sup 2+^1 }']
        for s in examples:
            cProfile.run('eqn(\'' + s + '\')')
