from typing import Any, Optional
import pytest
from func_adl import ObjectStream, EventDataset
import layered_edm as ledm
import ast


@pytest.fixture
def simple_ds() -> ObjectStream:
    class my_evt_ds(EventDataset):
        async def execute_result_async(
            self, a: ast.AST, title: Optional[str] = None
        ) -> Any:
            return a

    return my_evt_ds()


def test_ds_ds(simple_ds):
    @ledm.edm_sx
    class my_evt:
        @property
        @ledm.remap(lambda ds: ds.Select(lambda e: e.MissingET().First()))
        def met(self):
            ...

    data = my_evt(simple_ds)
    r = data.met

    assert "MissingET" in ast.dump(r)
