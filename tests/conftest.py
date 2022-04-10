import ast
from typing import Union
import sys

import pytest

# Hide ast.unparse
if sys.version_info < (3, 9):

    def unparse(node: Union[str, ast.AST]) -> str:
        if isinstance(node, str):
            return ast.dump(ast.parse(node).body[0].value)
        return ast.dump(node)

else:

    def unparse(node: Union[str, ast.AST]) -> str:
        if isinstance(node, str):
            return node
        return ast.unparse(node)


@pytest.fixture
def ak_behavior(mocker):
    the_dict = {}
    mocker.patch("layered_edm.util_types.ak.behavior", the_dict)
    return the_dict
