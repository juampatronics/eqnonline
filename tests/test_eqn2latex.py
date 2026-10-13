import unittest as ut
from pyroff.eqn2latex import Eqn2Latex, escape_chars


class EqnTests(ut.TestCase):
    def setUp(self):
        self.translator = Eqn2Latex()

    def _runtests(self, examples):
        for case, expected in examples:
            result = self.translator.translate(case)
            self.assertEqual(result, expected)

    def test_scripts(self):
        cases = [('x sup 2', r'x^{2}'),
                 ('sum from n=1 to N x sub i', r'\sum_{n=1}^{N} x_{i}'),
                 ('x over 2', r'\frac{x}{2}'),
                 ('{ a sup 2 } over { x+1 }', r'\frac{a^{2}}{x+1}'),
                 ('{ a sup { x+y } } over { x+1 }',
                     r'\frac{a^{x+y}}{x+1}'),
                 ('omega over lambda', r'\frac{\omega}{\lambda}'),
                 ('pi sub { sqrt 2 }', r'\pi_{\sqrt{2}}'),
                 ('x sup 2 sub 3', 'x^{2}_{3}'),
                 ('prod from i=0 to N sum from k=0 to K x sub k sup i',
                  r'\prod_{i=0}^{N} \sum_{k=0}^{K} x_{k}^{i}')]
        self._runtests(cases)

    def test_controlchars(self):
        cases = [(r'\sum', r'\\sum'),
                 (r'\hat{x_{\lambda}}', r'\\hat{x_{\\lambda}}'),
                 (r'\hat{x_{\lambda}}', r'\\hat{x_{\\lambda}}'),
                 (r'x_{\pi} & y^{\delta}', r'x_{\\pi} \& y^{\\delta}')]
        for case, expected in cases:
            self.assertEqual(escape_chars(case, r'\\&'), expected)
            self.assertEqual(escape_chars(case, [r'\\', '&']), expected)

    def test_symbols(self):
        cases = [('x -> inf', r'x \to \infty'),
                 ('x +- y', r'x \pm y'),
                 ('x != y', r'x \ne y')]

        self._runtests(cases)

    def test_bracketed(self):
        cases = [(r'left ( x sup 2 over 2  right )',
                  r'\left( \frac{x^{2}}{2} \right)'),
                 (r'left { x sup 2 over 2  right }',
                  r'\left{ \frac{x^{2}}{2} \right}'),
                 (r'left [ x sup 2 over 2  right ]',
                  r'\left[ \frac{x^{2}}{2} \right]')]
        self._runtests(cases)

    def test_spaces(self):
        cases = [('x sup 2^+^1', r'x^{2} \; + \; 1'),
                 ('x sup 2+~1', r'x^{2+} \quad 1')]
        self._runtests(cases)
