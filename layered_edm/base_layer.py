import inspect
from typing import Callable, Optional, Tuple, get_type_hints


class BaseEDMLayer:
    def __init__(self, template: object):
        self._template = template

    def _find_template_attr(self, name: str) -> Optional[Callable]:
        # Get the remapping function
        t = getattr(self._template, name, None)
        if t is None:
            return None
        l_callback = getattr(t.fget, "__remap_func", None)

        # See if we are a sub-object or not.
        # type_info = get_type_hints(t.fget)
        # Look at return annotation.
        return l_callback


def remap(l_func: Callable) -> Callable:
    """Wrap a property to redirect how the item is actually accessed

    ```
    @property
    @ledm.remap(lambda j: j.jet_px)
    def px(self) -> float:
        ...
    ```

    If the central dataset is called `ds` then, when you do `data.px` it
    will access `ds.jet_px` instead.

    Notes:
        * The `@property` must come before the `@ledm.remap`.

    Args:
        l_func (Callable): The lambda function to apply to the central
            datasource used in this template to render this property.

    Returns:
        Callable: Returns a function that can be used to wrap a property
        method.
    """

    def attach_lambda(p: property) -> property:
        # TODO make this work with property not just function
        # by looking at fget and setting it directly.
        # Or properly wrap properties or something
        # so we can chain them.
        p.__remap_func = l_func  # type: ignore
        return p

    return attach_lambda
