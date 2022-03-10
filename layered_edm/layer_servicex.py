from typing import Callable
import awkward as ak
from func_adl import ObjectStream
from .base_layer import BaseEDMLayer


class LEDMServiceX(BaseEDMLayer):
    def __init__(self, ds, edm_template: Callable):
        super().__init__(edm_template)
        self.ds = ds

    def __getattr__(self, __name: str) -> ak.Array:
        f = self._find_template_attr(__name)
        if f is not None:
            return f(self.ds).value()
        else:
            return getattr(self._array, __name)


def edm_sx(class_to_wrap: Callable) -> Callable:
    "Creates a class edm based on an servicex dataset. Nothing is implicit"

    def make_it(arr: ObjectStream):
        return LEDMServiceX(arr, class_to_wrap)

    return make_it
