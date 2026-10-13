import unittest as ut
from pyroff.pytbl import TblParser
from pyroff.ast import ASTNode, TokenNode


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
                     ASTNode('tblrow',
                             [ASTNode('cell', TokenNode('4')),
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
                     ASTNode('tblrow', [ASTNode('cell', TokenNode('4')),
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

    def test_noformat(self):
        expressions = ['''data1\tdata2
data3\tdata4''', '''allbox;
data1\tdata2''', '''c l.
data1\tdata2''']
        expected = [ASTNode('tbl',
                            [ASTNode('tblrow',
                                     [ASTNode('cell', TokenNode('data1')),
                                      ASTNode('cell', TokenNode('data2'))]),
                             ASTNode('tblrow',
                                     [ASTNode('cell', TokenNode('data3')),
                                      ASTNode('cell', TokenNode('data4'))])
                             ]),
                    ASTNode('tbl',
                            [ASTNode('tblformat',
                                     [ASTNode('option',
                                              [TokenNode('allbox')])]),
                             ASTNode('tblrow',
                                     [ASTNode('cell', TokenNode('data1')),
                                      ASTNode('cell', TokenNode('data2'))])
                             ]),
                    ASTNode('tbl',
                            [ASTNode('cellfmtline',
                                     [ASTNode('cellfmt', TokenNode('c')),
                                      ASTNode('cellfmt', TokenNode('l'))]),
                             ASTNode('tblrow',
                                     [ASTNode('cell', TokenNode('data1')),
                                      ASTNode('cell', TokenNode('data2'))])
                             ])
                    ]

        self._test_cases(expressions, expected)
