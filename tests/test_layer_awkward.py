# import pytest
from dataclasses import dataclass
from typing import Any, Callable, Iterable
import awkward as ak
import pytest
import layered_edm as ledm
from layered_edm.base_layer import BaseEDMLayer


@pytest.fixture
def simple_ds():
    return ak.Array(
        [
            [{"x": 1}, {"x": 2}, {"x": 3}],
            [],
            [{"x": 4}, {"x": 5}],
        ]
    )


def test_aw_in_layer(simple_ds):
    @ledm.edm_awk
    class my_evt:
        @property
        @ledm.remap(lambda e: e.x)
        def met(self):
            ...

    data = my_evt(simple_ds)
    r = data.met.ds

    assert isinstance(r, ak.Array)
    assert r.tolist() == [[1, 2, 3], [], [4, 5]]


class jet:
    @property
    def x(self) -> float:
        ...

    @property
    def y(self) -> float:
        ...

    @property
    def z(self) -> float:
        ...


def test_aw_jets_iterable(simple_ds):
    @ledm.edm_awk
    class my_evt:
        @property
        @ledm.remap()
        def p4(self) -> Iterable[jet]:
            ...

    data = my_evt(simple_ds)
    r = data.p4.x.ds

    assert isinstance(r, ak.Array)
    assert r.tolist() == [[1, 2, 3], [], [4, 5]]


def test_aw_jets_behavior_test(simple_ds):
    "Test adding a pre-existing, very simple, behavior"

    class awk_my_behavior(ak.Array):
        @property
        def x2(self):
            return self.x * 2

    @ledm.edm_awk
    @ledm.add_awk_behavior(awk_my_behavior)
    class my_evt:
        ...

    vector = ak.Array(
        [
            [{"x": 1, "y": 2, "z": 3}, {"x": 4, "y": 5, "z": 6}],
        ],
    )

    data = my_evt(vector)

    print(ak.type(data.ds.ds))

    assert ak.all(data.x2.as_awkward() == data.x.as_awkward() * 2)


def test_aw_jets_behavior_test_2(simple_ds):
    "Test adding a pre-existing, very simple, behavior"

    class awk_my_behavior_1(ak.Array):
        @property
        def x2(self):
            return self.x * 2

    class awk_my_behavior_2(ak.Array):
        @property
        def x3(self):
            return self.x * 3

    @ledm.edm_awk
    @ledm.add_awk_behavior(awk_my_behavior_1)
    @ledm.add_awk_behavior(awk_my_behavior_2)
    class my_evt:
        ...

    vector = ak.Array(
        [
            [{"x": 1, "y": 2, "z": 3}, {"x": 4, "y": 5, "z": 6}],
        ],
    )

    data = my_evt(vector)

    assert ak.all(data.x2.as_awkward() == data.x.as_awkward() * 2)
    assert ak.all(data.x3.as_awkward() == data.x.as_awkward() * 3)


def test_wrap_other_layer_in_awk_redirect():
    class my_other_layer(BaseEDMLayer):
        def __init__(self, given_data=None):
            @dataclass
            class data:
                x = [1, 2, 3]
                y = [3, 4, 5]

            if given_data is None:
                given_data = data()
            super().__init__(given_data)

        def wrap(self, s: Any) -> BaseEDMLayer:
            return my_other_layer(s)

        def single_item_map(self, callback: Callable) -> Any:
            return callback(self._ds)

        def as_awkward(self) -> ak.Array:
            if isinstance(self._ds, my_other_layer):
                raise NotImplementedError()
            return ak.Array(self._ds)

    @ledm.edm_awk
    class my_evt:
        @property
        @ledm.remap(lambda e: e.x + 1)
        def met(self):
            ...

    data = my_evt(my_other_layer())

    assert str(data.met.as_awkward()) == str(ak.Array([2, 3, 4]))


def test_wrap_other_layer_in_awk():
    class my_other_layer(BaseEDMLayer):
        def __init__(self, given_data=None):
            @dataclass
            class data:
                x = [1, 2, 3]
                y = [3, 4, 5]

            if given_data is None:
                given_data = data()
            super().__init__(given_data)

        def wrap(self, s: Any) -> BaseEDMLayer:
            return my_other_layer(s)

        def single_item_map(self, callback: Callable) -> Any:
            return callback(self._ds)

        def as_awkward(self) -> ak.Array:
            if isinstance(self._ds, my_other_layer):
                raise NotImplementedError()
            return ak.Array(self._ds)

    @ledm.edm_awk
    class my_evt:
        @property
        @ledm.remap(lambda e: e.x + 1)
        def met(self):
            ...

    data = my_evt(my_other_layer())

    assert str(data.y) == str(ak.Array([3, 4, 5]))


def test_aw_jets_behavior_by_name(simple_ds):
    "Test adding a pre-existing, very simple, behavior"

    class awk_my_behavior(ak.Array):
        @property
        def x2(self):
            return self.x * 2

    ak.behavior["test_aw_jets_behavior_by_name"] = awk_my_behavior

    @ledm.edm_awk
    @ledm.add_awk_behavior("test_aw_jets_behavior_by_name")
    class my_evt:
        ...

    vector = ak.Array(
        [
            [{"x": 1, "y": 2, "z": 3}, {"x": 4, "y": 5, "z": 6}],
        ],
    )

    data = my_evt(vector)

    print(ak.type(data.ds.ds))

    assert ak.all(data.x2.as_awkward() == data.x.as_awkward() * 2)


def test_aw_jets_behavior_by_name_bad(simple_ds):
    "Test adding a pre-existing, very simple, behavior"

    class awk_my_behavior(ak.Array):
        @property
        def x2(self):
            return self.x * 2

    with pytest.raises(ValueError) as e:

        @ledm.edm_awk
        @ledm.add_awk_behavior("test_aw_jets_behavior_by_name_bad")
        class my_evt:
            ...

    assert "test_aw_jets_behavior_by_name_bad" in str(e)
