import unittest as ut
from pyroff.ast import ASTNode, TokenNode


class TestASTNodes(ut.TestCase):
    def test_options(self):
        node = ASTNode('foo', 12)
        node['color'] = 'green'

        self.assertEqual(node._type, 'foo')
        self.assertEqual(node['color'], 'green')
        self.assertEqual(len(node._children), 1)
        node.add_children([3, 4])
        self.assertEqual(len(node._children), 3)

    def test_stringrepr(self):
        self.assertEqual(ASTNode('node', ['123']).__str__(), 'node: 123')
        self.assertEqual(TokenNode('123').__str__(), '(123)')
        self.assertEqual(ASTNode('node', TokenNode('123')).__str__(),
                         'node: (123)')

    def test_comparison(self):
        node = ASTNode('ast')
        node.add_children(TokenNode('token'))
        self.assertEqual(node, ASTNode('ast', TokenNode('token')))
        node.add_children(TokenNode('2nd_token'))
        self.assertEqual(node, ASTNode('ast',
                                       [TokenNode('token'),
                                        TokenNode('2nd_token')]))
