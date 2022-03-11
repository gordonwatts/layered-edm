from typing import Callable, Union
from func_adl import ObjectStream

from layered_edm.layer_nested import BaseTemplateEDMLayer
from .base_layer import BaseEDMLayer


class LEDMServiceX(BaseEDMLayer):
    def __init__(self, stream: ObjectStream):
        super().__init__(stream)

    def as_sx(self) -> ObjectStream:
        return self.ds

    def as_awkward(self):
        return self.ds.AsAwkwardArray().value()

    def wrap(self, s: ObjectStream):
        return LEDMServiceX(s)


# class LEDMServiceX(BaseEDMLayer):
#     def __init__(self, ds, edm_template: Callable):
#         super().__init__(edm_template)
#         self.ds = ds

#     def __getattr__(self, __name: str) -> ak.Array:
#         f = self._find_template_attr(__name)
#         if f is not None:
#             return f(self.ds).value()
#         else:
#             return getattr(self._array, __name)


def edm_sx(class_to_wrap: Callable) -> Callable:
    "Creates a class edm based on an servicex dataset."

    def make_it(arr: Union[ObjectStream, LEDMServiceX]):
        to_wrap = arr
        if isinstance(to_wrap, ObjectStream):
            to_wrap = LEDMServiceX(to_wrap)

        return BaseTemplateEDMLayer(to_wrap, class_to_wrap)

    return make_it
