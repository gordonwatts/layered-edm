import pytest
import awkward as ak
import layered_edm as ledm


@pytest.fixture
def awkward_one():
    return ak.Array(
        [
            [{"x": 1, "y": 1.1}, {"x": 2, "y": 2.2}, {"x": 3, "y": 3.3}],
            [],
            [{"x": 4, "y": 4.4}, {"x": 5, "y": 5.5}],
            [{"x": 6, "y": 6.6}],
            [{"x": 7, "y": 7.7}, {"x": 8, "y": 8.8}, {"x": 9, "y": 9.9}],
        ]
    )


def test_return_as_property_explicit(awkward_one):
    @ledm.edm_awk
    class my_edm:
        @property
        @ledm.remap(lambda a: a.x * 2)
        def my_x(self) -> ak.Array:
            ...

    data = my_edm(awkward_one)

    assert isinstance(data.my_x, ak.Array)
    assert data.my_x[0][0] == 2
    assert data.my_x[2][0] == 8


def test_return_as_property_implied(awkward_one):
    @ledm.edm_awk
    class my_edm:
        @property
        @ledm.remap(lambda a: a.x)
        def my_x(self) -> ak.Array:
            ...

    data = my_edm(awkward_one)

    assert isinstance(data.x, ak.Array)
    assert data.x[0][0] == 1
    assert data.x[2][0] == 4
