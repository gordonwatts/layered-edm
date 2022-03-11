from __future__ import annotations
from typing import Any, Callable, Optional


class BaseEDMLayer:
    "Base layer for the edm"

    def __init__(self, ds):
        self._ds = ds

    def __getattr__(self, __name: str) -> Any:
        return BaseEDMLayer(getattr(self._ds, __name))

    @property
    def ds(self):
        return self._ds

    def _get_expression(self):
        return self._ds


def remap(l_func: Optional[Callable] = None) -> Callable:
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
