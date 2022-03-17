# import pytest
from typing import Iterable
import awkward as ak
import pytest
import layered_edm as ledm

# @pytest.fixture
# def awkward_one():
#     return ak.Array(
#         [
#             [{"x": 1, "y": 1.1}, {"x": 2, "y": 2.2}, {"x": 3, "y": 3.3}],
#             [],
#             [{"x": 4, "y": 4.4}, {"x": 5, "y": 5.5}],
#             [{"x": 6, "y": 6.6}],
#             [{"x": 7, "y": 7.7}, {"x": 8, "y": 8.8}, {"x": 9, "y": 9.9}],
#         ]
#     )


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


# def test_return_as_property(awkward_one):
#     a = ledm.LEDMAwkward(awkward_one)
#     assert isinstance(a.x, ak.Array)
#     assert a.x[0][0] == 1
#     assert a.x[2][0] == 4


# def test_format(awkward_one):
#     a = ledm.LEDMAwkward(awkward_one)
#     x, fmt = a._get_attribute_unresolved("x")
#     assert fmt == "awk"
#     assert len(x) == 5
#     assert len(x[1]) == 0
#     assert x[2][0] == 4


# # def test_return_as_property_explicit(awkward_one):
# #     @ledm.edm_awk
# #     class my_edm:
# #         @property
# #         @ledm.remap(lambda a: a.x * 2)
# #         def my_x(self) -> ak.Array:
# #             ...

# #     data = my_edm(awkward_one)

# #     assert isinstance(data.my_x, ak.Array)
# #     assert data.my_x[0][0] == 2
# #     assert data.my_x[2][0] == 8


# # def test_return_as_property_implied(awkward_one):
# #     @ledm.edm_awk
# #     class my_edm:
# #         @property
# #         @ledm.remap(lambda a: a.x)
# #         def my_x(self) -> ak.Array:
# #             ...

# #     data = my_edm(awkward_one)

# #     assert isinstance(data.x, ak.Array)
# #     assert data.x[0][0] == 1
# #     assert data.x[2][0] == 4
