from __future__ import annotations

from dataclasses import dataclass, field

from .adapters.descript import CompositionRef, DescriptAdapter, DescriptProjectRef
from .models import VariantArtifact, VariantKind, VideoJob
from .prompts import PromptBook

VARIANT_NAMES: dict[VariantKind, str] = {
    "natural": "A Natural",
    "retention": "B Retention",
    "loop": "C Loop",
}


@dataclass
class WorkflowResult:
    project_id: str
    artifacts: list[VariantArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reused_project: bool = False
    reused_variants: bool = False


class DescriptWorkflowRunner:
    """Idempotent one-source -> named variants -> review renders coordinator.

    A restart must not create a second project merely because the process lost
    local memory. Durable IDs in ``VideoJob.metadata`` are treated as the source
    of truth and are verified by project inspection before more mutations occur.
    """

    def __init__(self, adapter: DescriptAdapter, prompts: PromptBook):
        self.adapter = adapter
        self.prompts = prompts

    def prepare_variants(self, job: VideoJob) -> str:
        project_id = str(job.metadata.get("descript_project_id", ""))
        if not project_id:
            raw_ref = self.adapter.create_project(job.source, f"RLE {job.job_id}")
            project_id = raw_ref.project_id
            job.metadata["descript_project_id"] = project_id
            job.touch()

        existing = self._canonical_compositions(project_id)
        if len(existing) == len(VARIANT_NAMES):
            self._persist_composition_map(job, existing)
            return project_id

        prompt = self.prompts.load("descript-multivariant.md") + (
            "\n\n## Job context\n"
            f"job_id: {job.job_id}\n"
            f"premise: {job.premise or 'infer from full footage'}\n"
            f"source_duration_seconds: {job.source_duration:.3f}\n"
        )
        self.adapter.edit(DescriptProjectRef(project_id), prompt)

        created = self._canonical_compositions(project_id)
        self._persist_composition_map(job, created)
        if "natural" not in created:
            raise RuntimeError("Descript edit completed but canonical `A Natural` composition is missing")
        job.touch()
        return project_id

    def publish_variants(
        self,
        job: VideoJob,
        *,
        kinds: tuple[VariantKind, ...] = ("natural", "retention", "loop"),
    ) -> WorkflowResult:
        project_id = str(job.metadata.get("descript_project_id", ""))
        if not project_id:
            raise RuntimeError("job has no descript_project_id; call prepare_variants first")

        result = WorkflowResult(project_id=project_id, reused_project=True)
        compositions = self._canonical_compositions(project_id)
        self._persist_composition_map(job, compositions)

        for kind in kinds:
            comp = compositions.get(kind)
            if comp is None:
                result.warnings.append(f"composition not found: {VARIANT_NAMES[kind]}")
                continue

            prior = self._published_artifact(job, kind, project_id, comp.id)
            if prior is not None:
                result.artifacts.append(prior)
                result.reused_variants = True
                continue

            published = self.adapter.publish(DescriptProjectRef(project_id, comp.id))
            artifact = VariantArtifact(
                kind=kind,
                project_id=project_id,
                composition_id=comp.id,
                share_url=published.get("share_url"),
                metadata={
                    "composition_name": VARIANT_NAMES[kind],
                    "duration": comp.duration,
                    "render_access": "unlisted",
                },
            )
            job.artifacts.append(artifact)
            result.artifacts.append(artifact)

        job.touch()
        return result

    def _canonical_compositions(self, project_id: str) -> dict[VariantKind, CompositionRef]:
        by_name = {comp.name.casefold().strip(): comp for comp in self.adapter.compositions(project_id)}
        found: dict[VariantKind, CompositionRef] = {}
        for kind, name in VARIANT_NAMES.items():
            comp = by_name.get(name.casefold())
            if comp is not None:
                found[kind] = comp
        return found

    @staticmethod
    def _persist_composition_map(job: VideoJob, comps: dict[VariantKind, CompositionRef]) -> None:
        job.metadata["descript_compositions"] = {
            kind: {"id": comp.id, "name": comp.name, "duration": comp.duration}
            for kind, comp in comps.items()
        }

    @staticmethod
    def _published_artifact(
        job: VideoJob,
        kind: VariantKind,
        project_id: str,
        composition_id: str,
    ) -> VariantArtifact | None:
        for artifact in job.artifacts:
            if (
                artifact.kind == kind
                and artifact.project_id == project_id
                and artifact.composition_id == composition_id
                and artifact.share_url
            ):
                return artifact
        return None
