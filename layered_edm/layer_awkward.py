from typing import Any, Callable, Optional, Union
import awkward as ak

from layered_edm.util_types import append_awk_behavior_to_class, class_behavior

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

    def iterable_map(self, callback: Callable) -> BaseEDMLayer:
        "Because everything is array operations, we just do this"
        return callback(self.ds)


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

    def iterable_map(self, callback: Callable) -> BaseEDMLayer:
        raise NotImplementedError()


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


def add_awk_behavior(
    behavior: Union[type, str], reg_function: Optional[Callable[[], None]] = None
) -> Callable:
    """A decorator to add an awkward behavior to a EDM class.

    You can add multiple behaviors, but only once per app right now!

    Args:
        behavior (type|str): Either the name of declared `ak.behavior` or
                the class of the actual behavior
        reg_function (Callable): A function to call to register the behavior.
                Only called just before it is needed during binding.

    Returns:
        Callable: Applied to the class by the decorator machinery in python.
    """

    def add_behavior(class_to_wrap: type) -> type:
        append_awk_behavior_to_class(class_to_wrap, behavior, reg_function)
        return class_to_wrap

    return add_behavior
