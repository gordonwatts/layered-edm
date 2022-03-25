import ast
from typing import Callable, Union

import awkward as ak
from func_adl import ObjectStream
from func_adl.util_ast import parse_as_ast

from layered_edm.layer_nested import BaseTemplateEDMLayer

from .base_layer import BaseEDMLayer

# TODO: the parse_as_ast should that be exported or put in a separate package?


class LEDMServiceX(BaseEDMLayer):
    def __init__(self, stream: ObjectStream):
        super().__init__(stream)

    def as_sx(self) -> ObjectStream:
        return self.ds

    def as_awkward(self):
        def generate():
            return self.ds.AsAwkwardArray().value()

        return ak.virtual(generate)

    def wrap(self, s: ObjectStream):
        return LEDMServiceX(s)

    def iterable_map(self, callback: Callable) -> BaseEDMLayer:
        "Simulate call on make loop"
        function_ast = parse_as_ast(callback, "remap")
        my_func = ast.parse("lambda items: items.Select(function_ast)").body[0].value  # type: ignore
        my_func.body.args[0] = function_ast
        return self.ds.Select(my_func)

    def single_item_map(self, callback: Callable) -> ObjectStream:
        "Call on a single item"

        # We can't pick it out, necessarily, so help the ast parser find it.
        function_ast = parse_as_ast(callback, "remap")

        return self.ds.Select(function_ast)


def edm_sx(class_to_wrap: Callable) -> Callable:
    "Creates a class edm based on an servicex dataset."

    def make_it(arr: Union[ObjectStream, LEDMServiceX]):
        to_wrap = arr
        if isinstance(to_wrap, ObjectStream):
            to_wrap = LEDMServiceX(to_wrap)

        return BaseTemplateEDMLayer(to_wrap, class_to_wrap)

    return make_it
