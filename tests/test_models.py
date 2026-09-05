import pytest
from rachel_loop_engine.models import SourceSpec

def test_source_validation():
    with pytest.raises(ValueError):
        SourceSpec(uri="x", duration_seconds=0)
