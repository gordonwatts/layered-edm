import layered_edm as ledm
import pytest
import awkward as ak

from layered_edm.base_layer import BaseEDMLayer


class simple_array_layer(BaseEDMLayer):
    def __init__(self, arr):
        super().__init__(None)
        self._arr = arr

    def __getattr__(self, __name: str) -> ak.Array:
        return ak.Array(self._arr)


@pytest.fixture
def dummy_layer():

    return simple_array_layer([1, 2, 3])


def test_nested(dummy_layer):
    @ledm.edm_nested
    class second_level:
        @property
        @ledm.remap(lambda ds: ds.forker * 2)
        def met(self):
            ...

    d = second_level(dummy_layer)
    assert len(d.met) == 3
    assert d.met[0] == 2
    assert d.met[1] == 4
    assert d.met[2] == 6


def test_defined_nested():
    @ledm.edm_nested
    class second_level:
        @property
        @ledm.remap(lambda ds: ds.forker * 2)
        def met(self):
            ...

    composite = ledm.nest(second_level, simple_array_layer)

    d = composite([2, 4, 6])
    assert len(d.met) == 3
    assert d.met[0] == 4
    assert d.met[1] == 8
    assert d.met[2] == 12
