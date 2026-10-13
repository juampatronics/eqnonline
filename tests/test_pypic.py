import unittest as ut

# PLY builds the lexer/parser out of the grammar definitions that are
# visible in the calling module's namespace, so re-export pyroff.pypic here.
from pyroff.pypic import *  # noqa: F401,F403
from pyroff.pypic import lex, yacc, reserved


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
        expected = [s[1:-1] for s in cases]
        self.run_tests(cases, expected, 'LABEL')

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
move left 1 from left of last circle; box
arrow from lower left of last ellipse to top of 1st box''']
        for txt in cases:
            self.pixer.input(txt)
            [t for t in self.pixer]


class TestParser(ut.TestCase):
    def setUp(self):
        self._parser = yacc.yacc(start='pic')

    def run_tests(self, examples, expected):
        for case, must in zip(examples, expected):
            print('about to parse: ' + case)
            t = self._parser.parse(case)
            print(t, ' expected ', must)
            self.assertEqual(t, must)

    def test_buildgrammar(self):
        # just checks that the grammar compiles
        pass

    def test_circle(self):
        examples = ['circle', 'down ; circle',
                    'circle radius 0.5', 'circle "ABC"',
                    'circle rad .5 "label 1" "label 2"']
        expected = [('primitive', ('circle', (None,))),
                    ('direction', ('down',), 'primitive', ('circle', (None,))),
                    ('primitive', ('circle', ('radius', (0.5,)))),
                    ('primitive', ('circle', ('label', ('ABC',)))),
                    ('primitive', ('circle', ('radius', (0.5,), 'label', ('label 1',),
                                              'label', ('label 2',))))]
        self.run_tests(examples, expected)

    def test_box(self):
        examples = ['box', 'box "label 1"',
                    'box height 1 width .5',
                    'box ht .75 "Square One"',
                    'box wid .5 "Second" "Square"',
                    'box dotted "klmmlkwe"']
        expected = [('primitive', ('box', (None,))),
                    ('primitive', ('box', ('label', ('label 1',)))),
                    ('primitive', ('box', ('height', (1.0,),
                                           'width', (0.5,)))),
                    ('primitive', ('box', ('height', (0.75,),
                                           'label', ('Square One',)))),
                    ('primitive', ('box', ('width', (0.5,), 'label', ('Second',),
                                           'label', ('Square',)))),
                    ('primitive', ('box', ('lstyle', ('dotted',),
                                           'label', ("klmmlkwe",))))]
        self.run_tests(examples, expected)

    def test_line(self):
        examples = ['line', 'line "a label" above']
        expected = [('primitive', ('line', (None,))),
                    ('primitive', ('line', ('label', ('a label',),
                                            'tposition', ('above',))))]
        self.run_tests(examples, expected)

    def _test_badgrammar(self):
        examples = ['circle 0.5']
        for s in examples:
            with self.assertRaises(yacc.YaccError):
                self._parser.parse(s)
