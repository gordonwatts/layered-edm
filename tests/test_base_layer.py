from __future__ import annotations
import layered_edm as ledm
from layered_edm.base_layer import BaseEDMLayer


def test_base_with_no_template():
    "Make sure a base layer with nothing still works"

    class empty_base(BaseEDMLayer):
        def __init__(self):
            super().__init__(None)

    eb = empty_base()
    assert eb._find_template_attr("hi") is None


class tracker:
    def __init__(self, stem: str):
        self._stem = stem

    def __getattr__(self, __name: str) -> tracker:
        return tracker(self._stem + "." + __name)

    @property
    def stem(self) -> str:
        return self._stem


class tracker_layer(BaseEDMLayer):
    def __init__(self):
        super().__init__(None)
        self._ds = tracker("ds")

    def __getattr__(self, name: str) -> tracker:
        f = self._find_template_attr(name)
        if f is not None:
            return f(self._ds)
        else:
            return getattr(self._ds, name)


class jet:
    @property
    @ledm.remap(lambda j: j.jet_px)
    def px(self):
        ...

    @property
    @ledm.remap(lambda j: j.jet_py)
    def py(self):
        ...


def test_sub_obj():
    "Go after nested properties with cascading re-maps"

    @ledm.edm_nested
    class event:
        @property
        @ledm.remap(lambda e: e.big_jet)
        def best_jet(self) -> jet:
            ...

    d = event(tracker_layer())
    r = d.best_jet.px
    assert r.stem == "ds.big_jet.jet_px"


def test_sub_obj_implied_structure():
    "Remap which should do nothing"

    class jet:
        @property
        @ledm.remap(lambda j: j.jet_px)
        def px(self):
            ...

        @property
        @ledm.remap(lambda j: j.jet_py)
        def py(self):
            ...

    @ledm.edm_nested
    class event:
        @property
        @ledm.remap()
        def best_jet(self) -> jet:
            ...

    d = event(tracker_layer())
    r = d.jets.px
    assert r.stem == "ds.jet_px"
