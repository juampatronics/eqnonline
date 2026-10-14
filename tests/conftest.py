"""Shared pytest fixtures for the pyroff test suite.

PLY keeps a single process-global lexer (``ply.lex.lexer``) that
``LRParser.parse()`` consults whenever no lexer object is passed in.  Each
grammar module builds its own lexer at import time (``pyroff.pyeqn.tokenizer``
and ``pyroff.pypic.tokenizer``) and the last import wins the global slot.
This suite runs both grammars in a single process, so point the global at the
tokenizer the test module under test actually needs.
"""
import pytest
import ply.lex
import pyroff.pyeqn as pyeqn
import pyroff.pypic as pypic

_LEXERS = {
    'test_eqn': pyeqn.tokenizer,
    'test_eqn2latex': pyeqn.tokenizer,
    'test_pyeqn': pyeqn.tokenizer,
    'test_server': pyeqn.tokenizer,
    'test_pypic': pypic.tokenizer,
}


@pytest.fixture(scope='module', autouse=True)
def ply_global_lexer(request):
    lexer = _LEXERS.get(request.module.__name__.rsplit('.', 1)[-1])
    if lexer is not None:
        ply.lex.lexer = lexer
    yield
