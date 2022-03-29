from typing import Any, Callable, Union
import awkward as ak

from layered_edm.util_types import class_behavior

from .layer_nested import BaseTemplateEDMLayer
from .base_layer import BaseEDMLayer


class LEDMAwkward(BaseEDMLayer):
    def __init__(self, awk_array: ak.Array):
        super().__init__(awk_array)

    def wrap(self, s: Any) -> BaseEDMLayer:
        return LEDMAwkward(s)

    def single_item_map(self, callback: Callable) -> Any:
        return callback(self.ds)

    def as_awkward(self):
        return self.ds

    def add_behavior(self, b_name: str):
        """Add a behavior to the awkward array.

        WARNING: call this only once. A second time and the
        first behavior will be forgotten!

        Args:
            b_name (str): The name of the new behavior to set us up as.
        """
        self._ds = ak.Array(self.ds, with_name=b_name)


class LEDMAwkwardConverter(BaseEDMLayer):
    """Capture another layer, and as we cross it, convert everything
    into an awkward layer.
    """

    def __init__(self, ds: BaseEDMLayer):
        super().__init__(None)

        self._captured_ds = ds

    def __getattr__(self, name: str) -> Any:
        "Access attributes on the captured guy, and convert to awk"
        return getattr(self._captured_ds, name).as_awkward()

    def wrap(self, s: Any) -> BaseEDMLayer:
        if isinstance(s, ak.Array):
            return LEDMAwkward(s)

        raise NotImplementedError()  # pragma: no cover

    def single_item_map(self, callback: Callable) -> Any:
        return callback(self)

    def as_awkward(self) -> ak.Array:
        raise NotImplementedError()  # pragma: no cover


def edm_awk(class_to_wrap: type) -> Callable:
    "Creates a class edm based on an awkward array"

    def make_it(arr: Union[ak.Array, LEDMAwkward]):
        to_wrap = arr

        if isinstance(to_wrap, ak.Array):
            # Raw awkward array!
            to_wrap = LEDMAwkward(to_wrap)

        if not isinstance(to_wrap, LEDMAwkward):
            # Convert from some non-awkward type
            to_wrap = LEDMAwkwardConverter(to_wrap)

        # Look for associated behaviors
        behaviors = class_behavior(class_to_wrap)
        if behaviors is not None:
            to_wrap.add_behavior(behaviors)

        # And create the base class
        return BaseTemplateEDMLayer(to_wrap, class_to_wrap)

    return make_it


def add_awk_behavior(behavior: Union[type, str]) -> Callable:
    """You can add multiple behaviors, but only once per app right now!

    Args:
        behavior (type): _description_

    Returns:
        Callable: _description_
    """

    if isinstance(behavior, str):
        type_behavior = ak.behavior.get(behavior, None)
        if type_behavior is None:
            raise ValueError(
                f"No behavior named {behavior} is declared to ak.behavior."
            )

    def add_behavior(cls: type) -> type:
        if not hasattr(cls, "_awk_behaviors"):
            setattr(cls, "_awk_behaviors", [])
        getattr(cls, "_awk_behaviors").append(behavior)
        return cls

    return add_behavior
