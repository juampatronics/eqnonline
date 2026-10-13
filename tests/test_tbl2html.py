import unittest as ut
import re
from pyroff.tbl2html import Tbl2Html


class TblTests(ut.TestCase):
    def setUp(self):
        self._translator = Tbl2Html()
        return self

    def _run_tests(self, expressions, expected):
        for case, should in zip(expressions, expected):
            result = self._translator.translate(case)
            self.assertEqual(re.sub('\s+', '', result),
                             re.sub('\s+', '', should))

    def test_basiccases(self):
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
            c c
            r r.
            vertically centered|User Console
            \^|Monochromatic graphics terminal
            \^|Touch screen
            \^|High resolution display''']

        expected = ['''<table style="border: none;"><tr>
            <td style="text-alignment : center;">1</td>
            <td style="text-alignment : left;">User Console</td></tr>
            <tr><td style="text-alignment : center;">2</td>
            <td style="text-alignment : left;">
            Monochromatic graphics terminal</td></tr>
            <tr><td style="text-alignment : center;">3</td>
            <td style="text-alignment : left;">Touch screen</td></tr>
            <tr><td style="text-alignment : center;">4</td>
            <td style="text-alignment : left;">High resolution display
            </td></tr></table>
            ''', '''<table style="text-align: center;border: 1px solid black;
            border: none;"><tr><td style="text-alignment : center;">1</td>
            <td style="text-alignment : left;">User Console</td></tr>
            <tr><td style="text-alignment : center;">2</td>
            <td style="text-alignment : left;">
            Monochromatic graphics terminal</td></tr>
            <tr><td style="text-alignment : center;">3</td>
            <td style="text-alignment : left;">Touch screen</td></tr>
            <tr><td style="text-alignment : center;">4</td>
            <td style="text-alignment : left;">High resolution display</td>
            </tr></table>
            ''', '''<table style="border: none;"><tr>
            <td style="text-alignment : center;">1</td>
            <td style="text-alignment : left;">User Console</td></tr>
            <tr><td style="text-alignment : right;">2</td>
            <td style="text-alignment : right;">
            Monochromatic graphics terminal</td></tr>
            <tr><td style="text-alignment : right;">3</td>
            <td style="text-alignment : right;">Touch screen</td></tr>
            <tr><td style="text-alignment : right;">4</td>
            <td style="text-alignment : right;">
            High resolution display</td></tr></table>
            ''', '''<table style="border: none;"><tr>
            <td style="text-alignment : center;" rowspan="4">
            vertically centered</td> <td style="text-alignment : center;">
            User Console</td></tr> <tr>
            <td style="text-alignment : right;">
            Monochromatic graphics terminal</td></tr> <tr>
            <td style="text-alignment : right;">Touch screen</td></tr>
            <tr> <td style="text-alignment : right;">
            High resolution display</td></tr></table>''']

        self._run_tests(expressions, expected)

    def test_colexpansion(self):
        expressions = ['''tab (@);
            c l.
            1@User Console
            2@Monochromatic graphics terminal
            3@Touch screen
            4@High resolution display''']

        expected = ['''<table style="border: none;">
            <tr><td style="text-alignment : center;">1</td>
            <td style="text-alignment : left;">User Console</td></tr>
            <tr><td style="text-alignment : center;">2</td>
            <td style="text-alignment : left;">Monochromatic graphics
            terminal </td></tr>
            <tr><td style="text-alignment : center;">3</td>
            <td style="text-alignment : left;">Touch screen</td></tr>
            <tr><td style="text-alignment : center;">4</td>
            <td style="text-alignment : left;">High resolution display</td>
            </tr></table>''']

        self._run_tests(expressions, expected)

    def test_font(self):
        expressions = ['''tab(|);
            cp12 rbi.
            first|second''']
        expected = ['''<table style="border: none;"><tr>
            <td style="text-alignment : center;font-size: 12px;">first</td>
            <td style="text-alignment : right;font-style: italic;
            font-weight: bold;">second</td></tr></table>''']

        self._run_tests(expressions, expected)

    def test_baredata(self):
        expressions = ['''data1\tdata2
data3\tdata4''']
        expected = ['''<table style="border: none;">
                    <tr><td>data1</td><td>data2</td></tr>
                    <tr><td>data3</td><td>data4</td></tr></table>''']

        self._run_tests(expressions, expected)
