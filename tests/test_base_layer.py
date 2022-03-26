from __future__ import annotations
from typing import Any, Callable
import layered_edm as ledm
from layered_edm.base_layer import BaseEDMLayer


def test_base_getattr():
    class c:
        @property
        def px(self):
            return 1

    # Base layer doesn't exist in the abstract, so we have to create a concrete version of it.
    class c_layer(BaseEDMLayer):
        def wrap(self, s: Any) -> BaseEDMLayer:
            return c_layer(s)

        def single_item_map(self, callback: Callable) -> Any:
            raise NotImplementedError()

    bl = c_layer(c())
    assert bl.px.ds == 1


class tracker:
    def __init__(self, stem: str):
        self._stem = stem

    def __getattr__(self, __name: str) -> tracker:
        return tracker(self._stem + "." + __name)

    @property
    def stem(self) -> str:
        return self._stem


class jet:
    @property
    @ledm.remap(lambda j: j.jet_px)
    def px(self):
        ...

    @property
    @ledm.remap(lambda j: j.jet_py)
    def py(self):
        ...
