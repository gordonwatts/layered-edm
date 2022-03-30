import ast
import sys

if sys.version_info < (3, 9):

    def unparse(a: ast.AST):
        "Unparse an ast"
        return ast.dump(a, annotate_fields=False)

else:

    def unparse(a: ast.AST):
        return ast.unparse(a)
