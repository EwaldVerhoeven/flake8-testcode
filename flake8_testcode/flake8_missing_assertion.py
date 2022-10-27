import ast
import sys
from typing import Any, Generator, Tuple, Type

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


TMA001 = 'TMA001 missing assertion in test'


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[tuple[int, int, str]] = []
        self._testcount = 0

    def _is_test(self, node: ast.FunctionDef) -> bool:
        if node.name[0:4].lower() == 'test':
            return True

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._is_test(node):
            assertion = False

            sub_nodes = ast.walk(node)
            col = {i for i in sub_nodes}
            # 1. Look for 'Assert' nodes in the abstract tree
            if any(isinstance(i, ast.Assert) for i in col):
                assertion = True
            # 2. Look for 'Attribute' nodes containing any assertions
            elif any(isinstance(i, ast.Attribute) for i in col):
                attributes = [i for i in col if isinstance(i, ast.Attribute)]
                for i in attributes:
                    if i.attr[0:6] == 'assert':
                        assertion = True

            if not assertion:
                self.errors.append((node.lineno, node.col_offset))

        self.generic_visit(node)


class Plugin:
    name = 'flake8-testcode'
    version = importlib_metadata.version('flake8_testcode')
    # version = '0.1.0'

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        for line, col in visitor.errors:
            yield line, col, TMA001, type(self)
