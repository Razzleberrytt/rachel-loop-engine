from __future__ import annotations
from typing import Any

class MockDescriptTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []
        self._n = 0
        self._jobs: dict[str, dict[str, Any]] = {}
        self._compositions = [{"id": "comp-raw", "name": "00 Raw", "duration": 20.0}, {"id": "comp-a", "name": "A Natural", "duration": 17.0}, {"id": "comp-b", "name": "B Retention", "duration": 14.0}, {"id": "comp-c", "name": "C Loop", "duration": 13.5}]
    def _new(self, result: dict[str, Any]) -> dict[str, Any]:
        self._n += 1
        job_id = f"job-{self._n}"
        self._jobs[job_id] = {"status": "success", "result": result}
        return {"job_id": job_id}
    def import_media(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("import_media", payload))
        return self._new({"project_id": "project-1", "composition_id": "comp-raw"})
    def run_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("run_agent", payload))
        prompt = str(payload.get("prompt", ""))
        if "RLE_REVIEW_JSON" in prompt:
            cid = payload.get("composition_id")
            score = {"comp-a": 90, "comp-b": 94, "comp-c": 92}.get(cid, 80)
            loop_seam = 4.3 if cid == "comp-c" else None
            import json
            review = {
                "passed": True,
                "overall_score": score,
                "story_truthfulness": 5,
                "hook_strength": 4.2,
                "pacing": 4.4,
                "caption_quality": 4.0,
                "audio_quality": 4.0,
                "loop_seam": loop_seam,
                "warnings": [],
                "notes": [],
            }
            return self._new({
                "project_id": payload["project_id"],
                "agent_response": "RLE_REVIEW_JSON\n" + json.dumps(review),
                "project_changed": False,
            })
        return self._new({"project_id": payload["project_id"]})
    def wait(self, job_id: str) -> dict[str, Any]:
        self.calls.append(("wait", job_id))
        return self._jobs[job_id]
    def get_project(self, project_id: str) -> dict[str, Any]:
        self.calls.append(("get_project", project_id))
        return {"project_id": project_id, "compositions": self._compositions}
    def publish(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("publish", payload))
        cid = payload.get("composition_id", "unknown")
        return self._new({"share_url": f"https://example.test/{cid}"})
