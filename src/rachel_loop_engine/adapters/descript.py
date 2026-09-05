from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .base import EditorTransport
from ..models import SourceSpec

@dataclass(frozen=True)
class DescriptProjectRef:
    project_id: str
    composition_id: str | None = None

@dataclass(frozen=True)
class CompositionRef:
    id: str
    name: str
    duration: float | None = None

class DescriptAdapter:
    def __init__(self, transport: EditorTransport, *, folder_name: str = "Rachel Loop Engine"):
        self.transport = transport
        self.folder_name = folder_name
    def create_project(self, source: SourceSpec, project_name: str) -> DescriptProjectRef:
        payload = {"project_name": project_name, "team_access": "edit", "folder_name": self.folder_name, "add_media": {source.filename: {"url": source.uri, "language": source.language}}, "add_compositions": [{"name": "00 Raw", "width": 1080, "height": 1920, "fps": 30, "clips": [{"media": source.filename}]}]}
        body = _result_body(self.transport.wait(_job_id(self.transport.import_media(payload))))
        project_id = body.get("project_id") or body.get("id")
        if not project_id:
            raise RuntimeError("Descript import completed without project_id")
        return DescriptProjectRef(project_id=str(project_id), composition_id=body.get("composition_id"))
    def agent(self, ref: DescriptProjectRef, prompt: str) -> dict[str, Any]:
        """Run the project agent and return its terminal result body."""
        payload: dict[str, Any] = {"project_id": ref.project_id, "prompt": prompt}
        if ref.composition_id:
            payload["composition_id"] = ref.composition_id
        return _result_body(self.transport.wait(_job_id(self.transport.run_agent(payload))))

    def edit(self, ref: DescriptProjectRef, prompt: str) -> dict[str, Any]:
        """Backward-compatible alias for mutation-oriented agent calls."""
        return self.agent(ref, prompt)
    def inspect(self, project_id: str) -> dict[str, Any]:
        return self.transport.get_project(project_id)
    def compositions(self, project_id: str) -> list[CompositionRef]:
        body = _result_body(self.inspect(project_id))
        out: list[CompositionRef] = []
        for item in body.get("compositions", []):
            cid = item.get("id") or item.get("composition_id")
            if cid:
                out.append(CompositionRef(id=str(cid), name=str(item.get("name", "")), duration=item.get("duration")))
        return out
    def find_composition(self, project_id: str, name: str) -> CompositionRef | None:
        target = name.casefold().strip()
        for comp in self.compositions(project_id):
            if comp.name.casefold().strip() == target:
                return comp
        return None
    def publish(self, ref: DescriptProjectRef, *, resolution: str = "1080p", access_level: str = "unlisted") -> dict[str, Any]:
        payload: dict[str, Any] = {"project_id": ref.project_id, "resolution": resolution, "media_type": "Video", "access_level": access_level}
        if ref.composition_id:
            payload["composition_id"] = ref.composition_id
        return _result_body(self.transport.wait(_job_id(self.transport.publish(payload))))

def _job_id(result: dict[str, Any]) -> str:
    job_id = result.get("job_id")
    if not job_id:
        raise RuntimeError("transport operation did not return job_id")
    return str(job_id)

def _result_body(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("status") == "error":
        raise RuntimeError(str(result.get("error") or result))
    body = result.get("result", result)
    if isinstance(body, dict) and body.get("status") == "error":
        raise RuntimeError(str(body.get("error") or body))
    return body if isinstance(body, dict) else {"value": body}
