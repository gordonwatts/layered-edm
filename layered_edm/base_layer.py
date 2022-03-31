from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

import awkward as ak


class BaseEDMLayer(ABC):
    "Base layer for the edm"

    def __init__(self, ds):
        self._ds = ds

    def __getattr__(self, __name: str) -> Any:
        """Playing at heuristics here and hoping this will
        return the right thing.

        Args:
            __name (str): _description_

        Returns:
            Any: _description_
        """
        return self.wrap(getattr(self._ds, __name))

    @property
    def ds(self):
        return self._ds

    def _get_expression(self):
        return self

    @abstractmethod
    def single_item_map(self, callback: Callable) -> Any:
        """Maps a single item by applying a transform on the current expression
        to convert to somethign new (e.g. apply a.x or like a Select).

        Args:
            callback (Callable): The lambda that applies the transform

        Returns:
            Any: Returns the object we are looking at
        """
        ...

    @abstractmethod
    def wrap(self, s: Any) -> BaseEDMLayer:
        """Wrap a new expression.

        Args:
            s (Any): The new expression to wrap

        Returns:
            BaseEDMLayer: The new expression
        """
        ...

    @abstractmethod
    def as_awkward(self) -> ak.Array:
        """Return an awkward array representation of this data.

        Make the array virtual if at all possible.

        Returns:
            ak.Array: array representation of the data
        """

    @abstractmethod
    def iterable_map(self, callback: Callable) -> BaseEDMLayer:
        """Return a new layer that is a map over some sequence - map function.

        Args:
            callback (Callable): Callback that supplies the map function

        Returns:
            BaseEDMLayer: The representative of the map function.
        """
        ...


def remap(l_func: Optional[Callable] = lambda a: a) -> Callable:
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
