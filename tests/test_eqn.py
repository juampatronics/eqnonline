import unittest as ut
from io import StringIO
from pyroff.eqn import InlineEqn, eqn, invalid_delim


class TestInlineExpressions(ut.TestCase):
    def setUp(self):
        self._compiler = InlineEqn('#', '#')

    def test_inline(self):
        code = 'Inlined as #x over 2#'
        result = self._compiler.compile(code)
        self.assertEqual(result, r'Inlined as #\frac{x}{2}#')

    def test_multiple(self):
        code = 'Inlined as #x over 2# and #x != y#'
        result = self._compiler.compile(code)
        self.assertEqual(result, r'Inlined as #\frac{x}{2}# and #x \ne y#')


class TestPreprocessor(ut.TestCase):
    def test_delim(self):
        code = '''.EQ
delim ##
.EN
Some text #pi sup 2#'''
        input = StringIO(code)
        output = StringIO()
        eqn(input, output)
        result = output.getvalue()
        self.assertEqual(result, 'Some text #\pi^{2}#')

    @ut.expectedFailure
    def test_baddelim(self):
        code = '''.EQ
delim {0}{0}
.EN
Some text {0}pi sup 2{0}'''
        for char in invalid_delim:
            input = StringIO(code.format(char))
            output = StringIO()
            eqn(input, output)
            result = output.getvalue()
            self.assertEqual(result, 'Some text #\pi^{2}#')

    def test_eqnblock(self):
        code = '''Some text
.EQ
x over 2
.EN
and more'''
        input = StringIO(code)
        output = StringIO()
        eqn(input, output)
        result = output.getvalue()
        self.assertEqual(result, '''Some text
.EQ
\\frac{x}{2}
.EN
and more''')
