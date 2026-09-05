from rachel_loop_engine.adapters import DescriptAdapter, MockDescriptTransport
from rachel_loop_engine.models import SourceSpec

def test_descript_happy_path():
    t = MockDescriptTransport()
    a = DescriptAdapter(t)
    ref = a.create_project(SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20), "RLE j1")
    assert ref.project_id == "project-1"
    a.edit(ref, "tighten it")
    published = a.publish(ref)
    assert published["share_url"].startswith("https://")
    names = [name for name, _ in t.calls]
    assert names.count("import_media") == 1
    assert names.count("run_agent") == 1
    assert names.count("publish") == 1
