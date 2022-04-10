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
    "Patch the awkward behavior dictionary in `util_types`"
    the_dict = {}
    mocker.patch("layered_edm.util_types.ak.behavior", the_dict)
    return the_dict


@pytest.fixture
def simple_ds():
    import awkward as ak

    return ak.Array(
        [
            [{"x": 1}, {"x": 2}, {"x": 3}],
            [],
            [{"x": 4}, {"x": 5}],
        ]
    )
