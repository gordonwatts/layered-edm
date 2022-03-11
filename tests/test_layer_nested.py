from dataclasses import dataclass
from typing import List
import pytest
from layered_edm.base_layer import BaseEDMLayer
import layered_edm as ledm
from layered_edm.layer_nested import BaseTemplateEDMLayer


class simple_array_layer(BaseEDMLayer):
    def __init__(self, arr):
        super().__init__(arr)


@dataclass
class single_item_test_data:
    forker: List[int]


@pytest.fixture
def dummy_layer():
    return simple_array_layer(single_item_test_data([1, 2, 3]))


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


# # def test_defined_nested():
# #     @ledm.edm_nested
# #     class second_level:
# #         @property
# #         @ledm.remap(lambda ds: ds.forker * 2)
# #         def met(self):
# #             ...

# #     composite = ledm.nest(second_level, simple_array_layer)

# #     d = composite([2, 4, 6])
# #     assert len(d.met) == 3
# #     assert d.met[0] == 4
# #     assert d.met[1] == 8
# #     assert d.met[2] == 12
