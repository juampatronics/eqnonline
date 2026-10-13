# -*- coding: utf-8 -*-
"""
Iterate over the AST

Copyright (C) 2020
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
import inspect
import re
from typing import List


class CompileException(RuntimeError):
    pass


def pairwise(iterable):
    'iterates over pairs (a0, a1), (a2, a3), ...'
    a = iter(iterable)
    return zip(a, a)


def process_ast(tree, callbacks):
    assert(tree is not None)
    assert(callbacks is not None)

    nodes = []
    for nodetype, args in pairwise(tree):
        transformed = process_ast(
            args, callbacks) if len(args) > 1 else args[0]
        if nodetype not in callbacks:
            raise CompileException('Undefined callback: ' + nodetype)
        if type(transformed) == tuple:
            nodes.append(callbacks[nodetype](*transformed))
        else:
            nodes.append(callbacks[nodetype](transformed))
    return tuple(nodes)


class Translator(object):
    def __init__(self, parser, keywords: List[str]):
        self._expected = keywords
        self._parser = parser

    def custom(self, module, prefix=None, debug=False):
        expected = self._expected
        parser = self._parser

        class Converter(object):
            def __init__(self, pymodule, prefix=None):
                self._parser = parser
                members = inspect.getmembers(pymodule)
                if prefix is not None:
                    self._callbacks = dict((re.sub(prefix, '', name), handler)
                                           for name, handler in members
                                           if re.sub(prefix, '', name)
                                           in expected)
                else:
                    self._callbacks = dict((name, handler)
                                           for name, handler in members if name
                                           in expected)

            def translate(self, s):
                t = self._parser.parse(s)
                return ' '.join(process_ast(t, self._callbacks))

            def translate_file(self, filename):
                with open(filename, 'r') as f:
                    return self.translate(self._parser.parse(f.readlines()))

        return Converter(module, prefix)
