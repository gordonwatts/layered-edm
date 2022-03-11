from typing import Any, Optional
import pytest
from func_adl import ObjectStream, EventDataset
import ast


@pytest.fixture
def simple_ds() -> ObjectStream:
    class my_evt_ds(EventDataset):
        async def execute_result_async(
            self, a: ast.AST, title: Optional[str] = None
        ) -> Any:
            return a

    return my_evt_ds()


# def test_ds_ds(simple_ds):
#     class my_evt:
#         @property
#         @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
#         def met(self):
#             ...

#     data = BaseTemplateEDMLayer(LEDMServiceX(simple_ds), my_evt, "sx")
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
