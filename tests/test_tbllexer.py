import unittest as ut
from pyroff.tbllexer import TblLexer, TblToken

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
one|two|three|four|five''']
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
\^|data4''', '''c _.
vertically centered\tUser Console''']
        expected_tokens = [
            [TblToken('DOUBLEBOX', 'doublebox'), TblToken('COMMA', ','),
             TblToken('TAB', '|'), TblToken('SEMICOLON', ';'),
             TblToken('FORMAT', 'c'), TblToken('FORMAT', 'c'),
             TblToken('ENDFMTLINE', '\n'),
             TblToken('FORMAT', '^'), TblToken('FORMAT', 'c'),
             TblToken('DOT', '.'),
             TblToken('TEXT', 'data1'), TblToken('TEXT', 'data2'),
             TblToken('NEWLINE', '\n'),
             TblToken('EMPTYCELL', r'\^'), TblToken('TEXT', 'data4')],
            [TblToken('FORMAT', 'c'), TblToken('FORMAT', '_'),
             TblToken('DOT', '.'), TblToken('TEXT', 'vertically centered'),
             TblToken('TEXT', 'User Console')]]
        self._test_cases(samples, expected_tokens)

    def test_textblock(self):
        samples = ['''data1\tT{this is
a block}T\tdata3
T{{}}T\t\^\t\^''']
        expected_tokens = [[TblToken('TEXT', 'data1'),
            TblToken('TEXT', '''this is
a block'''), TblToken('TEXT', 'data3'), TblToken('NEWLINE', '\n'),
            TblToken('TEXT', '{}'),
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
