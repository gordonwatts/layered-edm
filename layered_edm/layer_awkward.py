from typing import Callable
import awkward as ak
from .base_layer import BaseEDMLayer


class LEDMAwkward(BaseEDMLayer):
    def __init__(self, awk_array: ak.Array, edm_template: Callable):
        super().__init__(edm_template)
        self._array = awk_array

    def __getattr__(self, __name: str) -> ak.Array:
        f = self._find_template_attr(__name)
        if f is not None:
            return f(self._array)
        else:
            return getattr(self._array, __name)


def edm_awk(class_to_wrap: Callable) -> Callable:
    "Creates a class edm based on an awkward array"

    def make_it(arr: ak.Array):
        return LEDMAwkward(arr, class_to_wrap)

    return make_it
