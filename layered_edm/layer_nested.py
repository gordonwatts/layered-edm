# from __future__ import annotations
# from typing import Any, Callable, Optional
# from .base_layer import BaseEDMLayer
# from .layer_awkward import LEDMAwkward
# from .layer_servicex import LEDMServiceX
# import awkward as ak


# def convert_format(value: BaseEDMLayer, requested_format: str):
#     current_format = value.format
#     if current_format == requested_format:
#         return value.ds
#     if requested_format == "awk":
#         if current_format == "sx":
#             return LEDMAwkward(value.ds.value())
#     raise NotImplementedError(
#         f"Conversion from {current_format} to {requested_format} not implemented"
#     )


# def make_holder(value: Any, format: str) -> BaseEDMLayer:
#     if format == "awk":
#         return LEDMAwkward(value)
#     elif format == "sx":
#         return LEDMServiceX(value)
#     raise NotImplementedError(f"Format {format} not implemented")


# class BaseTemplateEDMLayer(BaseEDMLayer):
#     "Base layer when there is a template involved"

#     def __init__(self, wrapped: BaseEDMLayer, template: object, template_type: str):
#         super().__init__(wrapped, template_type)
#         self._template = template

#     def clone(self, new_obj):
#         raise RuntimeError()

#     def _get_attribute_unresolved(self, name: str) -> BaseEDMLayer:
#         mod_call = self._find_template_attr(name)
#         if mod_call is not None:
#             temp = make_holder(mod_call(self.ds.ds), self.ds.format)
#             local_value = convert_format(temp, self.format)
#             return make_holder(local_value, self.format)
#         raise NotImplementedError()

#     def __getattr__(self, __name: str) -> Any:
#         value = self._get_attribute_unresolved(__name)
#         holder = convert_format(value, "awk")
#         return holder.ds

#     def _find_template_attr(self, name: str) -> Optional[Callable]:
#         # Get the remapping function
#         t = getattr(self._template, name, None)
#         if t is None:
#             return None
#         l_callback = getattr(t.fget, "__remap_func", None)

#         #     # See if we are a sub-object or not.
#         #     # type_info = get_type_hints(t.fget)
#         #     # Look at return annotation.
#         return l_callback

#     # def __getattr__(self, __name: str) -> Any:
#     #     f = self._find_template_attr(__name)
#     #     if f is not None:
#     #         return f(self._ds)
#     #     return super().__getattr__(__name)


# class LEDMLayerNested(BaseEDMLayer):
#     def __init__(self, nested_layer: BaseEDMLayer, template: object, format: str):
#         super().__init__(template, format)
#         self._base_layer = nested_layer

#     def __getattr__(self, __name: str) -> ak.Array:
#         f = self._find_template_attr(__name)
#         if f is not None:
#             return f(self._base_layer)
#         else:
#             # Should climb the inheritance tree
#             return getattr(self._base_layer, __name)


# def edm_nested(class_to_wrap: Callable, format: str) -> Callable:
#     "Creates a class edm based on an servicex dataset. Nothing is implicit"

#     def make_it(layer: BaseEDMLayer):
#         return LEDMLayerNested(layer, class_to_wrap, format)

#     return make_it


# def nest(*class_chain):
#     def build_class(*args, **kwargs):
#         back_order = list(reversed(class_chain))
#         result = back_order[0](*args, *kwargs)
#         for cls in back_order[1:]:
#             result = cls(result)
#         return result

#     return build_class
