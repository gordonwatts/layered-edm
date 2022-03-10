from typing import Callable
from .base_layer import BaseEDMLayer
import awkward as ak


class LEDMLayerNested(BaseEDMLayer):
    def __init__(self, nested_layer: BaseEDMLayer, template: object):
        super().__init__(template)
        self._base_layer = nested_layer

    def __getattr__(self, __name: str) -> ak.Array:
        f = self._find_template_attr(__name)
        if f is not None:
            return f(self._base_layer)
        else:
            # Should climb the inheritance tree
            return getattr(self._base_layer, __name)


def edm_nested(class_to_wrap: Callable) -> Callable:
    "Creates a class edm based on an servicex dataset. Nothing is implicit"

    def make_it(layer: BaseEDMLayer):
        return LEDMLayerNested(layer, class_to_wrap)

    return make_it


def nest(*class_chain):
    def build_class(*args, **kwargs):
        back_order = list(reversed(class_chain))
        result = back_order[0](*args, *kwargs)
        for cls in back_order[1:]:
            result = cls(result)
        return result

    return build_class
