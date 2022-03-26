from typing import Any, Callable, Union
import awkward as ak

from .layer_nested import BaseTemplateEDMLayer
from .base_layer import BaseEDMLayer


def _get_behavior_name(behavior: type) -> str:
    return behavior.__name__


class LEDMAwkward(BaseEDMLayer):
    def __init__(self, awk_array: ak.Array):
        super().__init__(awk_array)

    def wrap(self, s: Any) -> BaseEDMLayer:
        return LEDMAwkward(s)

    def single_item_map(self, callback: Callable) -> Any:
        return callback(self.ds)

    def as_awkward(self):
        return self.ds

    def add_behavior(self, b: type):
        "Add awkward behavior to our array"
        b_name = _get_behavior_name(b)
        # TODO: Make this unique per array, not global, by using the
        #       `behavior` keyword argument.
        if ("*", b_name) not in ak.behavior:
            ak.behavior["*", b_name] = b
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


def edm_awk(class_to_wrap: Callable) -> Callable:
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
        if hasattr(class_to_wrap, "_awk_behaviors"):
            if len(class_to_wrap._awk_behaviors) == 1:
                to_wrap.add_behavior(class_to_wrap._awk_behaviors[0])
            else:

                class all_behaviors(*(class_to_wrap._awk_behaviors)):  # type: ignore
                    pass

                to_wrap.add_behavior(all_behaviors)

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
    else:
        type_behavior = behavior

    def add_behavior(cls: type) -> type:
        if not hasattr(cls, "_awk_behaviors"):
            setattr(cls, "_awk_behaviors", [])
        getattr(cls, "_awk_behaviors").append(type_behavior)
        return cls

    return add_behavior
