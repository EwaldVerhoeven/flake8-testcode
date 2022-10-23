import ast
from typing import Set
from flake8_assertion_checker import Plugin


def _results(code: str) -> Set[str]:
    tree = ast.parse(code)
    plugin = Plugin(tree)
    return {f'{line}:{col} {msg}' for line, col, msg, _ in plugin.run()}


def test_trivial_case() -> None:
    assert _results('def f():pass') == set()


def test_no_assertion_required() -> None:
    code = '''def my_func(self) -> None:
                my_value = 1
            '''
    assert _results(code) == set()


def test_missing_assertion() -> None:
    code = '''def test_my_func(self) -> None:
                my_value = 1
            '''
    assert _results(code) == {'1:0 TMA001 missing assertion in test'}


def test_included_assertion() -> None:
    code = '''def test_my_func(self) -> None:
                assert my_value == 1
            '''
    assert _results(code) == set()


def test_included_nested_assertion() -> None:
    code = '''def test_my_func(self) -> None:
                if 1 > 0:
                    assert 1 == 1
            '''
    assert _results(code) == set()


def test_missing_nested_assertion() -> None:
    code = '''def test_my_func(self) -> None:
                if 1 > 0:
                    var = 1
            '''
    assert _results(code) == {'1:0 TMA001 missing assertion in test'}


def test_included_assertion_stlb() -> None:
    code = '''def test_sum(self):
                self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
            '''
    assert _results(code) == set()


def test_included_double_nested_assertion_stlb() -> None:
    code = '''def test_sum(self):
                for i in [1, 2, 3]:
                    if 1 > 0:
                        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
            '''
    assert _results(code) == set()


def test_missing_assertion_double_nested_tree() -> None:
    code = '''def test_sum(self):
                for i in [1, 2, 3]:
                    if 1 > 0:
                        var = 1
            '''
    assert _results(code) == {'1:0 TMA001 missing assertion in test'}
