from __future__ import annotations
from dataclasses import dataclass, field
from .adapters.descript import DescriptAdapter, DescriptProjectRef
from .models import VariantArtifact, VariantKind, VideoJob
from .prompts import PromptBook

VARIANT_NAMES: dict[VariantKind, str] = {"natural": "A Natural", "retention": "B Retention", "loop": "C Loop"}

@dataclass
class WorkflowResult:
    project_id: str
    artifacts: list[VariantArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

class DescriptWorkflowRunner:
    def __init__(self, adapter: DescriptAdapter, prompts: PromptBook):
        self.adapter = adapter
        self.prompts = prompts
    def prepare_variants(self, job: VideoJob) -> str:
        raw_ref = self.adapter.create_project(job.source, f"RLE {job.job_id}")
        prompt = self.prompts.load("descript-multivariant.md") + f"\n\n## Job context\njob_id: {job.job_id}\npremise: {job.premise or 'infer from full footage'}\nsource_duration_seconds: {job.source_duration:.3f}\n"
        self.adapter.edit(DescriptProjectRef(raw_ref.project_id), prompt)
        job.metadata["descript_project_id"] = raw_ref.project_id
        job.touch()
        return raw_ref.project_id
    def publish_variants(self, job: VideoJob, *, kinds: tuple[VariantKind, ...] = ("natural", "retention", "loop")) -> WorkflowResult:
        project_id = str(job.metadata.get("descript_project_id", ""))
        if not project_id:
            raise RuntimeError("job has no descript_project_id; call prepare_variants first")
        result = WorkflowResult(project_id=project_id)
        for kind in kinds:
            name = VARIANT_NAMES[kind]
            comp = self.adapter.find_composition(project_id, name)
            if comp is None:
                result.warnings.append(f"composition not found: {name}")
                continue
            published = self.adapter.publish(DescriptProjectRef(project_id, comp.id))
            artifact = VariantArtifact(kind=kind, project_id=project_id, composition_id=comp.id, share_url=published.get("share_url"), metadata={"composition_name": name, "duration": comp.duration})
            job.artifacts.append(artifact)
            result.artifacts.append(artifact)
        job.touch()
        return result
