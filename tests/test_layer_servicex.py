import ast
from typing import Any, Iterable, Optional

import awkward as ak
import layered_edm as ledm
import pytest
from func_adl import EventDataset, ObjectStream
from layered_edm.layer_servicex import LEDMServiceX

from .conftest import unparse


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
def simple_ds2() -> ObjectStream:
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
        def __init__(self):
            super().__init__()
            self._count = 0

        @property
        def count(self) -> int:
            return self._count

        async def execute_result_async(
            self, a: ast.AST, _title: Optional[str] = None
        ) -> Any:
            self._count += 1
            return ak.Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    return my_evt_ds()


@pytest.fixture
def simple_awk_ds_virtual() -> ObjectStream:
    "Returns an awk array that is virtual"

    class my_evt_ds(EventDataset):
        def __init__(self):
            super().__init__()
            self._count = 0

        @property
        def count(self) -> int:
            return self._count

        async def execute_result_async(
            self, a: ast.AST, _title: Optional[str] = None
        ) -> Any:
            self._count += 1

            def generate():
                return ak.Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

            return ak.virtual(generate)

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

    assert unparse(r.value()) == unparse(
        "Select(EventDataset(), lambda e: e.MissingET().First())"
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
    assert simple_awk_ds.count == 0
    r = data.met.as_awkward()
    assert isinstance(r, ak.Array)
    assert len(r) == 10
    assert simple_awk_ds.count == 1


def test_as_awk_logging(simple_awk_ds, caplog):
    import logging

    logging.basicConfig()
    logger = logging.getLogger("layered_edm")
    logger.setLevel(logging.DEBUG)

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
    data.met.as_awkward()

    assert len(caplog.text) > 0


def test_as_awk_virtual(simple_awk_ds_virtual):
    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
        def met(self):
            ...

    @ledm.edm_sx
    class empty_evt:
        ...

    data = my_evt(empty_evt(simple_awk_ds_virtual))
    assert simple_awk_ds_virtual.count == 0
    r = data.met.as_awkward()
    assert isinstance(r, ak.Array)
    assert len(r) == 10
    assert simple_awk_ds_virtual.count == 1


def test_as_awk_repr(simple_awk_ds):
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
    assert repr(data.met.as_awkward()) == repr(ak.Array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))


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

    assert unparse(r.value()) == unparse(expected.value())


def test_simple_collection_as_awk(simple_awk_ds):
    "Test a collection of objects connected"

    class jet:
        @property
        @ledm.remap(lambda e: e.px())
        def px(self) -> float:
            ...

        @property
        @ledm.remap(lambda e: e.py())
        def py(self) -> float:
            ...

    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda e: e.subs())
        def subs(self) -> Iterable[jet]:
            ...

    data = my_evt(simple_awk_ds)
    awk_data = data.subs.as_awkward()
    # 1 because the first item had to be generated
    assert simple_awk_ds.count == 1

    assert len(awk_data.px) == 10
    assert simple_awk_ds.count == 1
    assert len(awk_data.py) == 10
    assert simple_awk_ds.count == 1

    assert isinstance(awk_data, ak.Array)
    t = ak.type(awk_data)
    assert t.length == 10
    assert t.keys() == ["px", "py"]
    assert len(awk_data) == 10
    assert simple_awk_ds.count == 2


def test_simple_collection_awk_behavior(simple_awk_ds):
    "Add awk behavior to a collection"

    class my_behavior(ak.Array):
        @property
        def px2(self):
            return 2 * self.px

    @ledm.add_awk_behavior(my_behavior)
    class my_jet:
        @property
        @ledm.remap(lambda e: e.px())
        def px(self) -> float:
            ...

        @property
        @ledm.remap(lambda e: e.py())
        def py(self) -> float:
            ...

    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda e: e.subs())
        def subs(self) -> Iterable[my_jet]:
            ...

    data = my_evt(simple_awk_ds)
    awk_data = data.subs.as_awkward()
    assert str(awk_data.px * 2) == str(awk_data.px2)
