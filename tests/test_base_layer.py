from __future__ import annotations
import layered_edm as ledm
from layered_edm.base_layer import BaseEDMLayer


def test_base_getattr():
    class c:
        @property
        def px(self):
            return 1

    bl = BaseEDMLayer(c())
    assert bl.px.ds == 1


# def test_base_template_same(mocker):

#     # Create the wrapper around the servicex calling thing
#     sx_base = mocker.MagicMock()
#     bl = BaseEDMLayer(sx_base, "sx")

#     class template:
#         @property
#         @ledm.remap(lambda events: events.Select(lambda e: e.met))
#         def met(self):
#             ...

#     nl = BaseTemplateEDMLayer(bl, template, "sx")
#     o = nl.met
#     assert not isinstance(o, BaseEDMLayer)
#     # Looking for sx_base.Select(...).value()
#     assert sx_base.Select.call_count == 1
#     sx_select = sx_base.Select.return_value
#     assert sx_select.value.call_count == 1


# def test_base_template_awk_conversion(mocker):

#     # Create the wrapper around the servicex calling thing
#     sx_base = mocker.MagicMock()
#     bl = BaseEDMLayer(sx_base, "sx")

#     class template1:
#         @property
#         @ledm.remap(lambda events: events.Select(lambda e: {"met": e.met}))
#         def met(self):
#             ...

#     class template2:
#         @property
#         @ledm.remap(lambda arr: arr.met)
#         def met(self):
#             ...

#     nl = BaseTemplateEDMLayer(
#         BaseTemplateEDMLayer(bl, template1, "sx"), template2, "awk"
#     )
#     o = nl.met
#     assert not isinstance(o, BaseEDMLayer)
#     # Looking for sx_base.Select(...).value().met
#     assert sx_base.Select.call_count == 1
#     sx_select = sx_base.Select.return_value
#     assert sx_select.value.call_count == 1


class tracker:
    def __init__(self, stem: str):
        self._stem = stem

    def __getattr__(self, __name: str) -> tracker:
        return tracker(self._stem + "." + __name)

    @property
    def stem(self) -> str:
        return self._stem


# class tracker_layer(BaseEDMLayer):
#     def __init__(self):
#         super().__init__(None)
#         self._ds = tracker("ds")

#     def __getattr__(self, name: str) -> tracker:
#         f = self._find_template_attr(name)
#         if f is not None:
#             return f(self._ds)
#         else:
#             return getattr(self._ds, name)


class jet:
    @property
    @ledm.remap(lambda j: j.jet_px)
    def px(self):
        ...

    @property
    @ledm.remap(lambda j: j.jet_py)
    def py(self):
        ...


# def test_sub_obj():
#     "Go after nested properties with cascading re-maps"

#     @ledm.edm_nested
#     class event:
#         @property
#         @ledm.remap(lambda e: e.big_jet)
#         def best_jet(self) -> jet:
#             ...

#     d = event(tracker_layer())
#     r = d.best_jet.px
#     assert r.stem == "ds.big_jet.jet_px"


# def test_sub_obj_implied_structure():
#     "Remap which should do nothing"

#     class jet:
#         @property
#         @ledm.remap(lambda j: j.jet_px)
#         def px(self):
#             ...

#         @property
#         @ledm.remap(lambda j: j.jet_py)
#         def py(self):
#             ...

#     @ledm.edm_nested
#     class event:
#         @property
#         @ledm.remap()
#         def best_jet(self) -> jet:
#             ...

#     d = event(tracker_layer())
#     r = d.jets.px
#     assert r.stem == "ds.jet_px"
