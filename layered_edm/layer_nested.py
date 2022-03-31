from typing import Any, Callable, Optional, Tuple, Type, get_args, get_type_hints

import awkward as ak

from layered_edm.base_layer import BaseEDMLayer
from layered_edm.util_types import class_behavior, is_iterable


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

    def __init__(self, wrapped: BaseEDMLayer, template: type):
        super().__init__(wrapped)
        self._template: type = template
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
        new_expr = self._make_expr_call(mod_call)
        new_expr_wrapped = expr.wrap(new_expr)

        # If the return type is not a simple type (float, int), then we need to
        # create a new template so we can follow it!
        if rtn_type is not None and not _is_terminal(rtn_type):
            if is_iterable(rtn_type):
                args = get_args(rtn_type)
                return IterableTemplateEDMLayer(new_expr_wrapped, args[0])
            else:
                return BaseTemplateEDMLayer(new_expr_wrapped, rtn_type)

        return new_expr_wrapped

    def _make_expr_call(self, callback: Callable) -> BaseEDMLayer:
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

    def iterable_map(self, callback: Callable) -> BaseEDMLayer:
        raise NotImplementedError()

    def as_awkward(self) -> ak.Array:
        """Generate awkward array for a single object (e.g not a collection)

        Returns:
            ak.Array: The resulting info
        """
        behavior_name = class_behavior(self._template)

        # Determine the length so that we do not cause everything to be generated
        # on creation.
        all_items = [item for item in dir(self._template) if not item.startswith("_")]
        assert len(all_items) > 0, "Template has no items"

        first_item = getattr(self, all_items[0]).as_awkward()
        n_items = len(first_item)

        items = {
            item: ak.virtual(
                lambda: ak.repartition(getattr(self, item).as_awkward(), None),
                length=n_items,
            )
            for item in all_items[1:]
        }

        items[all_items[0]] = ak.virtual(
            lambda: ak.repartition(first_item, None), length=n_items
        )

        # Build the array
        return ak.Array(
            items,
            with_name=behavior_name,
        )


class IterableTemplateEDMLayer(BaseTemplateEDMLayer):
    "Wrap a template that deals with a collection (list, etc.) of a particular data type"
    ...

    def __init__(self, wrapped: BaseEDMLayer, template: type):
        super().__init__(wrapped, template)

    def _make_expr_call(self, callback: Callable) -> BaseEDMLayer:
        expr = self._get_expression()
        return expr.iterable_map(callback)
