from __future__ import annotations

from dataclasses import dataclass, field

from .adapters.descript import CompositionRef, DescriptAdapter, DescriptProjectRef
from .models import JobStatus, QcResult, VariantArtifact, VariantKind, VideoJob
from .prompts import PromptBook
from .review import MediaReview, parse_media_review, recommend_variant, review_to_dict

VARIANT_NAMES: dict[VariantKind, str] = {
    "natural": "A Natural",
    "retention": "B Retention",
    "loop": "C Loop",
}


@dataclass
class TreatmentResult:
    project_id: str
    reviews: list[MediaReview] = field(default_factory=list)
    artifacts: list[VariantArtifact] = field(default_factory=list)
    recommended_variant: VariantKind | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    project_id: str
    artifacts: list[VariantArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reused_project: bool = False
    reused_variants: bool = False


class DescriptWorkflowRunner:
    """Idempotent one-source -> named variants -> QC -> review renders coordinator."""

    def __init__(self, adapter: DescriptAdapter, prompts: PromptBook):
        self.adapter = adapter
        self.prompts = prompts

    def full_treatment(
        self,
        job: VideoJob,
        *,
        publish_all_passing: bool = True,
    ) -> TreatmentResult:
        """Run the canonical one-input transaction from source to review renders.

        Rendering happens only after media-aware QC. Failed variants are never
        rendered by this method.
        """
        job.status = JobStatus.EDITING
        job.touch()
        project_id = self.prepare_variants(job)

        job.status = JobStatus.QC
        job.touch()
        reviews = self.review_variants(job)
        recommendation = recommend_variant(reviews)
        passing = [r.kind for r in reviews if r.passed]
        if not passing or recommendation is None:
            job.status = JobStatus.FAILED
            job.metadata["failure_reason"] = "no variant passed media-aware QC"
            job.touch()
            return TreatmentResult(
                project_id=project_id,
                reviews=reviews,
                recommended_variant=None,
                warnings=["No variant passed media-aware QC; nothing was rendered."],
            )

        render_kinds = tuple(passing) if publish_all_passing else (recommendation,)
        job.status = JobStatus.EXPORTING
        job.touch()
        published = self.publish_variants(job, kinds=render_kinds)
        job.status = JobStatus.COMPLETE
        job.metadata.pop("failure_reason", None)
        job.touch()
        return TreatmentResult(
            project_id=project_id,
            reviews=reviews,
            artifacts=published.artifacts,
            recommended_variant=recommendation,
            warnings=published.warnings,
        )

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
            artifact = self._artifact_for_composition(job, kind, project_id, comp.id)
            if artifact is None:
                artifact = VariantArtifact(kind=kind, project_id=project_id, composition_id=comp.id)
                job.artifacts.append(artifact)
            artifact.share_url = published.get("share_url")
            artifact.metadata.update(
                {
                    "composition_name": VARIANT_NAMES[kind],
                    "duration": comp.duration,
                    "render_access": "unlisted",
                }
            )
            result.artifacts.append(artifact)

        job.touch()
        return result

    def review_variants(
        self,
        job: VideoJob,
        *,
        kinds: tuple[VariantKind, ...] = ("natural", "retention", "loop"),
    ) -> list[MediaReview]:
        """Ask the editor agent to inspect finished compositions without mutation."""
        project_id = str(job.metadata.get("descript_project_id", ""))
        if not project_id:
            raise RuntimeError("job has no descript_project_id; call prepare_variants first")
        compositions = self._canonical_compositions(project_id)
        base_prompt = self.prompts.load("descript-qc-review.md")
        reviews: list[MediaReview] = []
        for kind in kinds:
            comp = compositions.get(kind)
            if comp is None:
                continue
            prompt = base_prompt + f"\n\n## Runtime target\nvariant_kind: {kind}\ncomposition_name: {VARIANT_NAMES[kind]}\n"
            before = comp
            result = self.adapter.agent(DescriptProjectRef(project_id, comp.id), prompt)
            after = self.adapter.find_composition(project_id, VARIANT_NAMES[kind])
            if after is None:
                raise RuntimeError(f"media-aware QC removed or renamed canonical composition: {VARIANT_NAMES[kind]}")
            if _duration_changed(before.duration, after.duration):
                raise RuntimeError(
                    f"media-aware QC changed composition duration for {VARIANT_NAMES[kind]}: "
                    f"{before.duration} -> {after.duration}"
                )
            response = str(result.get("agent_response", ""))
            review = parse_media_review(response, kind)
            reviews.append(review)
            artifact = self._artifact_for_composition(job, kind, project_id, comp.id)
            if artifact is None:
                artifact = VariantArtifact(kind=kind, project_id=project_id, composition_id=comp.id)
                job.artifacts.append(artifact)
            artifact.qc = QcResult(
                passed=review.passed,
                score=review.overall_score,
                failures=[] if review.passed else ["media-aware QC failed"],
                warnings=review.warnings,
            )
            artifact.metadata["media_review"] = review_to_dict(review)
            artifact.metadata["qc_agent_reported_project_changed"] = bool(result.get("project_changed", False))
            artifact.metadata["qc_fingerprint_stable"] = True
        job.metadata["recommended_variant"] = recommend_variant(reviews)
        job.touch()
        return reviews

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
    def _artifact_for_composition(
        job: VideoJob,
        kind: VariantKind,
        project_id: str,
        composition_id: str,
    ) -> VariantArtifact | None:
        for artifact in job.artifacts:
            if artifact.kind == kind and artifact.project_id == project_id and artifact.composition_id == composition_id:
                return artifact
        return None

    @staticmethod
    def _published_artifact(
        job: VideoJob,
        kind: VariantKind,
        project_id: str,
        composition_id: str,
    ) -> VariantArtifact | None:
        artifact = DescriptWorkflowRunner._artifact_for_composition(job, kind, project_id, composition_id)
        return artifact if artifact is not None and artifact.share_url else None


def _duration_changed(before: float | None, after: float | None, tolerance: float = 0.05) -> bool:
    if before is None or after is None:
        return before != after
    return abs(float(before) - float(after)) > tolerance
