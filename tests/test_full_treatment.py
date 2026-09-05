import json
from pathlib import Path

from rachel_loop_engine.adapters import DescriptAdapter, MockDescriptTransport
from rachel_loop_engine.models import JobStatus, SourceSpec, VideoJob
from rachel_loop_engine.prompts import PromptBook
from rachel_loop_engine.workflow import DescriptWorkflowRunner


def _runner(transport):
    return DescriptWorkflowRunner(DescriptAdapter(transport), PromptBook(Path(__file__).parents[1]))


def test_full_treatment_reviews_before_render_and_completes():
    t = MockDescriptTransport()
    runner = _runner(t)
    job = VideoJob(job_id="full", source=SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20))
    result = runner.full_treatment(job)
    assert job.status == JobStatus.COMPLETE
    assert result.recommended_variant == "retention"
    assert len(result.artifacts) == 3
    assert len(job.artifacts) == 3
    call_names = [name for name, _ in t.calls]
    first_publish = call_names.index("publish")
    last_review_agent = max(
        i for i, (name, payload) in enumerate(t.calls)
        if name == "run_agent" and "RLE_REVIEW_JSON" in str(payload.get("prompt", ""))
    )
    assert last_review_agent < first_publish


def test_full_treatment_does_not_render_failed_variants():
    class FailingLoopTransport(MockDescriptTransport):
        def run_agent(self, payload):
            result = super().run_agent(payload)
            if "RLE_REVIEW_JSON" in str(payload.get("prompt", "")) and payload.get("composition_id") == "comp-c":
                job_id = result["job_id"]
                raw = self._jobs[job_id]["result"]
                review = {
                    "passed": False,
                    "overall_score": 98,
                    "story_truthfulness": 5,
                    "hook_strength": 5,
                    "pacing": 5,
                    "caption_quality": 5,
                    "audio_quality": 5,
                    "loop_seam": 1.5,
                    "warnings": ["obvious loop seam"],
                    "notes": [],
                }
                raw["agent_response"] = "RLE_REVIEW_JSON\n" + json.dumps(review)
            return result

    t = FailingLoopTransport()
    runner = _runner(t)
    job = VideoJob(job_id="full", source=SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20))
    result = runner.full_treatment(job)
    assert job.status == JobStatus.COMPLETE
    assert {a.kind for a in result.artifacts} == {"natural", "retention"}
    published_comp_ids = [payload.get("composition_id") for name, payload in t.calls if name == "publish"]
    assert "comp-c" not in published_comp_ids
