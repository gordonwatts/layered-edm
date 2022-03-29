from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

import awkward as ak
import layered_edm as ledm
import pytest
from layered_edm.base_layer import BaseEDMLayer
from layered_edm.layer_nested import BaseTemplateEDMLayer


class simple_array_layer(BaseEDMLayer):
    def __init__(self, arr):
        super().__init__(arr)

    def wrap(self, arr):
        return simple_array_layer(arr)

    def iterable_map(self, callback: Callable) -> BaseEDMLayer:
        "Simulate call on make loop"
        return simple_array_layer(self.ds.make_loop(callback))

    def single_item_map(self, callback: Callable) -> BaseEDMLayer:
        "Call on a single item"
        return callback(self.ds)

    def as_awkward(self) -> ak.Array:
        return ak.Array([1, 2, 3, 4, 5])


@dataclass
class single_item_test_data:
    forker: List[int]


@pytest.fixture
def dummy_layer():
    return simple_array_layer(single_item_test_data([1, 2, 3]))


@pytest.fixture
def mock_layer(mocker):
    return simple_array_layer(mocker.MagicMock())


def test_nested(dummy_layer):
    "A very simple nesting"

    class second_level:
        @property
        @ledm.remap(lambda ds: ds.forker)
        def met(self):
            ...

    d = BaseTemplateEDMLayer(dummy_layer, second_level)
    assert len(d.met.ds) == 3
    assert d.met.ds[0] == 1
    assert d.met.ds[1] == 2
    assert d.met.ds[2] == 3


def test_nested_pass_thru(dummy_layer):
    "A very simple nesting"

    class second_level:
        @property
        @ledm.remap(lambda ds: ds["forker"])
        def met(self):
            ...

    d = BaseTemplateEDMLayer(dummy_layer, second_level)
    assert len(d.forker.ds) == 3
    assert d.forker.ds[0] == 1


class _test_sub_obj_remap:
    @property
    @ledm.remap(lambda so: so.my_prop())
    def my_prop(self) -> float:
        ...


def test_sub_object_remap_top_level(mock_layer):
    "A sub object with a single item"

    class main_obj:
        @property
        @ledm.remap()
        def sub(self) -> _test_sub_obj_remap:
            ...

    d = BaseTemplateEDMLayer(mock_layer, main_obj)
    result = d.sub.my_prop

    assert isinstance(result, simple_array_layer)
    mock_layer.ds.my_prop.assert_called_once()


def test_sub_object_remap_top_level_as_awk(mock_layer):
    "A sub object with a single item"

    class main_obj:
        @property
        @ledm.remap()
        def sub(self) -> _test_sub_obj_remap:
            ...

    d = BaseTemplateEDMLayer(mock_layer, main_obj)
    result = d.sub.as_awkward()

    assert len(result) == 5
    assert str(result.my_prop) == str(ak.Array([1, 2, 3, 4, 5]))


def test_sub_object_remap(mock_layer):
    "A sub object with a single item"

    class main_obj:
        @property
        @ledm.remap(lambda ds: ds.sub_objs())
        def sub(self) -> _test_sub_obj_remap:
            ...

    d = BaseTemplateEDMLayer(mock_layer, main_obj)
    result = d.sub.my_prop

    assert isinstance(result, simple_array_layer)
    mock_layer.ds.sub_objs.assert_called_once()
    mock_layer.ds.sub_objs.return_value.my_prop.assert_called_once()


def test_sub_object_remap_iterable(mock_layer, mocker):
    "A sub object with a single item"

    class main_obj:
        @property
        @ledm.remap()
        def subs(self) -> Iterable[_test_sub_obj_remap]:
            ...

    d = BaseTemplateEDMLayer(mock_layer, main_obj)
    result = d.subs.my_prop

    assert isinstance(result, simple_array_layer)
    mock_layer.ds.make_loop.assert_called_once()

    r = mocker.MagicMock()
    mock_layer.ds.make_loop.call_args_list[0][0][0](r)
    r.my_prop.assert_called_once()


def test_sub_object_remap_collection(mock_layer, mocker):
    "A sub object with a single item"

    class main_obj:
        @property
        @ledm.remap()
        def subs(self) -> Iterable[_test_sub_obj_remap]:
            ...

    d = BaseTemplateEDMLayer(mock_layer, main_obj)
    result = d.subs.as_awkward()

    assert isinstance(result, ak.Array)
