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


from typing import Any, Callable, Optional, Tuple, Type, get_args, get_type_hints

from layered_edm.base_layer import BaseEDMLayer
from layered_edm.util_types import is_iterable


def _is_terminal(t: Type) -> bool:
    """If the type is a simple terminal (like a float) and not another
    complex object we know about - like a class - then return false.

    Args:
        t (Type): The type to check

    Returns:
        bool: True if it is a terminal type, False otherwise
    """
    if t in [float, int, str]:
        return True
    return False


class BaseTemplateEDMLayer(BaseEDMLayer):
    "Wrap a template that deals with a particular data type"

    def __init__(self, wrapped: BaseEDMLayer, template: object):
        super().__init__(wrapped)
        self._template = template
        self._expression: Optional[BaseEDMLayer] = None

    def _get_expression(self) -> BaseEDMLayer:
        """Returns the expression that represents this layer.

        Returns:
            BaseEDMLayer: The expression representing this layer.
        """
        if self._expression is None:
            self._expression = self.ds._get_expression()
        return self._expression

    def __getattr__(self, name: str) -> Any:
        """Get the attribute, using the template as a mapping.
        If we can't find it, then we will let whatever we wrap try.

        Args:
            name (str): The name of the attribute to find

        Returns:
            Any: Result of fetching the attribute
        """
        mod_call, rtn_type = self._find_template_attr(name)
        if mod_call is None:
            return getattr(self.ds, name)

        # Now, call remapping function. To do this we need the current
        # expression we are working on, and then wrap it back up.
        expr = self._get_expression()
        new_expr = self._make_expr_call(expr.ds, mod_call)
        new_expr_wrapped = expr.wrap(new_expr)

        # If the return type is not a simple object, then we need to
        # create a new template so we can follow it!
        if rtn_type is not None and not _is_terminal(rtn_type):
            if is_iterable(rtn_type):
                args = get_args(rtn_type)
                return IterableTemplateEDMLayer(new_expr_wrapped, args[0])
            else:
                return BaseTemplateEDMLayer(new_expr_wrapped, rtn_type)

        return new_expr_wrapped

    def _make_expr_call(self, expr: BaseEDMLayer, callback: Callable) -> BaseEDMLayer:
        """Make a call to a remapping function.

        Args:
            expr (BaseEDMLayer): The expression to call the remapping function on
            callback (Callable): The remapping function

        Returns:
            BaseEDMLayer: The result of the remapping function
        """
        expr = self._get_expression()
        return expr.single_item_map(callback)

    def _find_template_attr(
        self, name: str
    ) -> Tuple[Optional[Callable], Optional[Type]]:
        """Find some sort of remapping function for a given attribute from the
        template.

        1. A remap function attached to a template attribute
        1. Return None

        Args:
            name (str): The attribute name

        Returns:
            Optional[Callable]: If a remapping function is found, this will be it. None otherwise.
        """
        t = getattr(self._template, name, None)
        if t is None:
            return None, None
        l_callback = getattr(t.fget, "__remap_func", None)

        # Get type hints back in case we are going for a second type of object for return.
        hints = get_type_hints(t.fget)
        rtn_type = hints.get("return", None)

        return l_callback, rtn_type

    def wrap(self, s: Any) -> BaseEDMLayer:
        raise RuntimeError("Should never need to wrap a template class")

    def single_item_map(self, callback: Callable) -> Any:
        raise RuntimeError("Should not be mapping a single item in a template")


class IterableTemplateEDMLayer(BaseTemplateEDMLayer):
    "Wrap a template that deals with a collection (list, etc.) of a particular data type"
    ...

    def __init__(self, wrapped: BaseEDMLayer, template: object):
        super().__init__(wrapped, template)

    def _make_expr_call(self, expr: BaseEDMLayer, callback: Callable) -> BaseEDMLayer:
        expr = self._get_expression()
        return expr.iterable_map(callback)


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
