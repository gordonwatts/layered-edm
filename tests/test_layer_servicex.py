import ast
from typing import Any, Iterable, Optional

import awkward as ak
import layered_edm as ledm
import pytest
from func_adl import EventDataset, ObjectStream
from layered_edm.layer_servicex import LEDMServiceX


@pytest.fixture
def simple_ds() -> ObjectStream:
    "Returns the ast when value() is called"

    class my_evt_ds(EventDataset):
        async def execute_result_async(
            self, a: ast.AST, _title: Optional[str] = None
        ) -> Any:
            return a

    return my_evt_ds()


@pytest.fixture
def simple_awk_ds() -> ObjectStream:
    "Returns the a dummy awkward when value() is called"

    class my_evt_ds(EventDataset):
        async def execute_result_async(
            self, a: ast.AST, _title: Optional[str] = None
        ) -> Any:
            return ak.Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    return my_evt_ds()


@pytest.fixture
def simple_ds2() -> ObjectStream:
    "Returns the ast when value() is called"

    class my_evt_ds(EventDataset):
        async def execute_result_async(
            self, a: ast.AST, _title: Optional[str] = None
        ) -> Any:
            return a

    return my_evt_ds()


def test_sx_empty_layer(simple_ds):
    @ledm.edm_sx
    class my_evt:
        ...

    data = my_evt(simple_ds)
    with pytest.raises(AttributeError) as e:
        data.met

    assert "met" in str(e)


def test_sx_wrap(simple_ds, simple_ds2):
    @ledm.edm_sx
    class my_evt:
        ...

    data = my_evt(simple_ds).ds
    data2 = data.wrap(simple_ds2)

    assert isinstance(data2, LEDMServiceX)
    assert data2.ds is simple_ds2


def test_sx_in_layer(simple_ds):
    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda e: e.MissingET().First())
        def met(self):
            ...

    @ledm.edm_sx
    class empty_evt:
        ...

    data = my_evt(empty_evt(simple_ds))
    r = data.met.ds

    assert (
        ast.unparse(r.value())
        == "Select(EventDataset(), lambda e: e.MissingET().First())"
    )


def test_as_sx(simple_ds):
    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
        def met(self):
            ...

    @ledm.edm_sx
    class empty_evt:
        ...

    data = my_evt(empty_evt(simple_ds))
    r = data.met.as_sx()
    assert isinstance(r, ObjectStream)


def test_as_awk(simple_awk_ds):
    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
        def met(self):
            ...

    @ledm.edm_sx
    class empty_evt:
        ...

    data = my_evt(empty_evt(simple_awk_ds))
    r = data.met.as_awkward()
    assert isinstance(r, ak.Array)
    assert len(r) == 10


class _test_sub_objs:
    @property
    @ledm.remap(lambda so: so.prop())
    def p(self):
        ...


def test_sub_sx(simple_ds):
    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda e: e.subs())
        def subs(self) -> Iterable[_test_sub_objs]:
            ...

    data = my_evt(simple_ds)
    r = data.subs.p.ds

    # fmt: off
    expected = (
        simple_ds
        .Select(lambda e: e.subs())
        .Select(lambda items: items.Select(lambda so: so.prop()))
    )
    # fmt: on

    assert ast.unparse(r.value()) == ast.unparse(expected.value())


# def test_2layer(simple_ds):
#     @ledm.sx_layer
#     class my_evt:
#         @property
#         @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
#         def met(self):
#             ...

#     data = my_evt(simple_ds)
#     r = data.met

#     assert ast.unparse(r) == "Select(EventDataset(), lambda e: e.MissingET().First())"


# def test_ds_nested_single_column(simple_ds):
#     class jet:
#         @property
#         @ledm.remap(lambda j: j.pt())
#         def pt(self) -> float:
#             ...

#     class my_evt:
#         @property
#         @ledm.remap(lambda ds: ds.Select(lambda e: e.Jets()))
#         def jets(self) -> Iterable[jet]:
#             ...

#     data = BaseTemplateEDMLayer(LEDMServiceX(simple_ds), my_evt, "sx")
#     r = data.jet.pt

#     assert (
#         ast.unparse(r)
#         == "Select(EventDataset(), lambda e: e.Jets()).Select(lambda jets: jets.Select(lambda j: j.pt()))"
#     )


# def test_ds_nested_single_column_no_depth(simple_ds):
#     class jet:
#         @property
#         @ledm.remap(lambda ds: ds.Select(lambda e: [j.pt() for j in e.Jets()]))
#         def pt(self) -> float:
#             ...

#     class my_evt:
#         @property
#         @ledm.remap()
#         def jets(self) -> Iterable[jet]:
#             ...

#     data = BaseTemplateEDMLayer(LEDMServiceX(simple_ds), my_evt, "sx")
#     r = data.jet.pt

#     assert (
#         ast.unparse(r)
#         == "Select(EventDataset(), lambda e: e.Jets()).Select(lambda jets: jets.Select(lambda j: j.pt()))"
#     )


# def test_ds_nested_all_columns(simple_ds):
#     class jet:
#         @property
#         @ledm.remap(lambda j: j.pt())
#         def pt(self) -> float:
#             ...

#         @property
#         @ledm.remap(lambda j: j.pz())
#         def pz(self) -> float:
#             ...

#     class my_evt:
#         @property
#         @ledm.remap(lambda ds: ds.Select(lambda e: e.Jets()))
#         def jets(self) -> Iterable[jet]:
#             ...

#     data = BaseTemplateEDMLayer(LEDMServiceX(simple_ds), my_evt, "sx")
#     r = data.jet

#     assert (
#         ast.unparse(r) == "Select(EventDataset(), lambda e: e.Jets())"
#         ".Select(lambda jets: {'pt': jets.Select(lambda j: j.pt()), "
#         "'pz': jets.Select(lambda j: j.pz()))"
#     )


# def test_sx_met_as_sx(simple_ds):
#     class my_evt:
#         @property
#         @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
#         def met(self):
#             ...

#     data = BaseTemplateEDMLayer(LEDMServiceX(simple_ds), my_evt, "sx")
#     r = data.met.as_sx("sx")

#     assert isinstance(r, ObjectStream)
#     assert (
#         ast.unparse(r.value())
#         == "Select(EventDataset(), lambda e: e.MissingET().First())"
#     )
