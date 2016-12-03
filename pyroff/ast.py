# -*- coding: utf-8 -*-
"""
ast.py A generic parse tree implementation, providing facility
routines for translation and diagnosing.

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

import re
import inspect


class ASTNode(object):
    '''Class to represent each node of the AST, which does not necessarily
       correspond to a token.
       You may add additional (meta-)information in the dictionary _options.
       This information is then passed to the callbacks as named parameters.
       See TranslatorFactory for more information.'''
    def __init__(self, nodetype, children=None, options=None):
        self._type = nodetype
        if not children:
            self._children = []
        else:
            self._children = [children] if not hasattr(children, '__len__') \
                                        else children
        self._options = options if options else {}

    def __str__(self):
        return self._type + ': ' + ', '.join(child.__str__()
                                             for child in self._children)

    def keys(self):
        return self._options.keys()

    def has_key(self, k):
        return k in self._options

    def get(self, key, default=None):
        if key not in self._options:
            return default
        return self._options[key]

    def __getitem__(self, key):
        return self._options[key]

    def __setitem__(self, key, value):
        self._options[key] = value

    def __delitem__(self, key):
        del self._options[key]

    def __repr__(self):
        return self.__str__()

    # comparison operators for testing
    def __eq__(self, other):
        if self._type != other._type:
            return False
        if len(self._children) != len(other._children):
            return False
        for i in range(len(self._children)):
            if self._children[i] != other._children[i]:
                return False
        return True

    def __neq__(self, other):
        return not self.__eq__(other)

    def add_children(self, children):
        'Adds new nodes to the current one'
        if type(children) == list:
            self._children += children
        else:
            self._children.append(children)
        return self

    def push_children(self, children):
        'Adds new nodes to the current one'
        if type(children) == list:
            self._children = children + self._children
        else:
            self._children.insert(0, children)
        return self

    def is_empty(self):
        return len(self._children) == 0

    def process_ast(self, callbacks, ignore_missing=False):
        '''Processes the AST tree beginning at the current node.  With the
        parameter ignore_missing the choose not to throw an exception when
        some node types have no corresponding callbacks.  The rationale is
        that in some cases you may be interested in some particular nodes
        only.
        '''
        if self._type not in callbacks and not ignore_missing:
            raise Exception('missing callback for node type ', self._type)
        result =  [child.process_ast(callbacks, ignore_missing)
                                     for child in self._children]
        return callbacks[self._type](*filter(lambda x: x is not None, result),
                                     meta=self._options)


class TokenNode(ASTNode):
    '''At the leaves of the AST, the TokenNode encodes the actual value.'''
    def __init__(self, value):
        if value is None:
            raise Exception('Input argument "value" must hold some value.')
        super(TokenNode, self).__init__('token', [value])

    def __str__(self):
        return '(' + ', '.join(self._children) + ')'

    def process_ast(self, callbacks, ignore_missing=False):
        return ' '.join(self._children)


class TreeTransverser(object):
    'This class is ment for internal use only.'
    def __init__(self, parser):
        self._parser = parser
        self._preproc = None
        self._postproc = None

    def translate(self, s, ignore=False):
        string = ''
        if self._preproc:
            string = self._preproc()
        ast = self._parser.parse(s)
        string +=  ' '.join(filter(lambda x: x is not None,
                (node.process_ast(self._callbacks, ignore) for node in ast)))
        return string + self._postproc() if self._postproc else string

    def translate_file(self, filename):
        with open(filename, 'r') as f:
            return translate(self.parse('\n'.join(f.readlines())))


class TranslatorFactory(object):
    '''This class provides an API for coding transformations of the tbl parse
    tree (AST). There are two kind of nodes, TokenNode and ASTNode. The first
    codes the leaves of the tree (that is, specific instatiations of a token),
    and the second syntax expressions.
    The encoded values are passed as positional arguments to the callback, and
    the metainformation as named arguments.
    In some cases, you may need to do some work before and/or after the tree
    has been transversed. TranslatorFactory looks for either two functions (in
    case of a module) or methods (in case of a class) named preproc and
    postproc, resp.
    For an example, please refer to tbl2html.py.
    '''
    def __init__(self, parser, prefix):
        self._parser = parser
        self._prefix = prefix

    def from_module(self, module):
        class Converter(TreeTransverser):
            def __init__(self, pymodule, prefix, expected, parser):
                super(Converter, self).__init__(parser)
                members = inspect.getmembers(pymodule)
                self._callbacks = dict((re.sub(prefix, '', name), handler)
                    for name, handler in members
                    if re.sub(prefix, '', name) in expected)

                for name, handler in members:
                    if name == 'preproc':
                        self._preproc = handler
                    elif name == 'postproc':
                        self._postproc = handler

        return Converter(module, self._prefix, self.expected, self._parser)

    def from_class(self, instance):
        class Converter(TreeTransverser):
            def __init__(self, instance, prefix, expected, parser):
                super(Converter, self).__init__(parser)
                members = dir(instance)
                self._callbacks = dict((re.sub(prefix, '', name),
                                        instance.__getattribute__(name))
                    for name in members
                    if re.sub(prefix, '', name) in expected)

                if 'preproc' in members:
                    self._preproc = instance.__getattribute__('preproc')
                elif 'postproc' in members:
                    self._postproc = instance.__getattribute__('postproc')

        return Converter(instance, self._prefix, self.expected, self._parser)

if __name__ == "__main__":
    import unittest as ut

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
            self.assertEqual(node,
                ASTNode('ast', [TokenNode('token'), TokenNode('2nd_token')]))

    ut.main()
