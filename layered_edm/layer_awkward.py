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


def edm_awk(class_to_wrap: Callable) -> Callable:
    "Creates a class edm based on an awkward array"

    def make_it(arr: Union[ak.Array, LEDMAwkward]):
        to_wrap = arr
        if isinstance(to_wrap, ak.Array):
            to_wrap = LEDMAwkward(to_wrap)
        if hasattr(class_to_wrap, "_awk_behaviors"):
            if len(class_to_wrap._awk_behaviors) == 1:
                to_wrap.add_behavior(class_to_wrap._awk_behaviors[0])
            else:

                class all_behaviors(*(class_to_wrap._awk_behaviors)):  # type: ignore
                    pass

                to_wrap.add_behavior(all_behaviors)

        return BaseTemplateEDMLayer(to_wrap, class_to_wrap)

    return make_it


def add_awk_behavior(behavior: type) -> Callable:
    """You can add multiple behaviors, but only once per app right now!

    Args:
        behavior (type): _description_

    Returns:
        Callable: _description_
    """

    def add_behavior(cls: type) -> type:
        if not hasattr(cls, "_awk_behaviors"):
            setattr(cls, "_awk_behaviors", [])
        getattr(cls, "_awk_behaviors").append(behavior)
        return cls

    return add_behavior
