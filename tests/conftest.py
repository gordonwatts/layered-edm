import ast
from typing import Union
import sys

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
