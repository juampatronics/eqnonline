# -*- coding: utf-8 -*-
"""
pic2svg.py converts eqn code into LaTeX

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
from .pypic import treebuilder
import sys


def pic_circle(*args):
    print('circle: ', *args)
    return '<circle {} />'.format(' '.join(args))


def pic_radius(*args):
    print('radius: ', *args)
    return 'r="{}"'.format(*args)


class Pic2SVG:
    def __init__(self, web=True):
        self._translator = treebuilder.custom(sys.modules[__name__], 'pic_')
        if web:
            self._header = '<svg xmlns="http://www.w3.org/2000/svg">'
        else:
            self._header += '''<?xml version = "1.0" encoding = "UTF-8" standalone = "no"?>
  <svg xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   version="1.0">'''
        self._footer = '</svg>'

    def translate(self, s):
        return '{}\n{}\n{}'.format(
            self._header, self._translator.translate(s), self._footer)

    def translate_file(self, filename):
        return self._translator.translate_file(filename)


if __name__ == "__main__":
    compiler = Pic2SVG()
    print(compiler.translate('circle radius 0.5'))
