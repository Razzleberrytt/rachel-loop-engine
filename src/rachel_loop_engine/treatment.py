from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json

from .adapters.ffmpeg import FfmpegAdapter
from .edl import LocalEditPlan, dump_plan
from .fingerprint import CreativeFingerprint, fingerprint_from_plan
from .local_workflow import LocalTreatmentResult, LocalWorkflowRunner
from .media import MediaInfo, MediaProbe
from .models import VideoJob
from .planner import build_hypothesis_variants, build_match_loop_plan, retained_segments
from .seam_hunter import MatchSeamCandidate, SeamCandidate, SeamHunter
from .social import SocialCopy, fallback_social_copy


@dataclass
class AutoTreatmentConfig:
    remove_ranges: list[tuple[float, float]] = field(default_factory=list)
    compression_remove_ranges: list[tuple[float, float]] = field(default_factory=list)
    retention_head_trim: float = 0.0
    loop_anchor: float | None = None
    payoff_range: tuple[float, float] | None = None
    alternate_hook_range: tuple[float, float] | None = None
    primary_text: str | None = None
    include_no_text_variant: bool = True
    auto_hunt_loop: bool = True
    include_match_loop: bool = True
    minimum_rotation_score: float = 55.0
    minimum_match_score: float = 84.0
    content_class: str = "unknown"
    hook_type: str = "unknown"
    motion_level: str = "unknown"


@dataclass
class OneButtonTreatmentResult:
    media: MediaInfo
    seam_candidates: list[SeamCandidate]
    match_candidates: list[MatchSeamCandidate]
    plans: dict[str, LocalEditPlan]
    local: LocalTreatmentResult
    fingerprints: dict[str, CreativeFingerprint]
    ranking: list[tuple[str, float]]
    recommended_variant: str | None
    loop_preview: str | None
    social_copy: SocialCopy
    report_path: str
    warnings: list[str] = field(default_factory=list)


class OneButtonTreatmentRunner:
    """Private source -> inspect -> plan -> render -> QC -> fingerprint -> register."""

    def __init__(
        self,
        *,
        probe: MediaProbe | None = None,
        seam_hunter: SeamHunter | None = None,
        local_workflow: LocalWorkflowRunner | None = None,
        ffmpeg: FfmpegAdapter | None = None,
    ) -> None:
        self.probe = probe or MediaProbe()
        self.seams = seam_hunter or SeamHunter(probe=self.probe)
        self.ffmpeg = ffmpeg or FfmpegAdapter(probe=self.probe)
        self.local = local_workflow or LocalWorkflowRunner(adapter=self.ffmpeg)

    def run(
        self,
        job: VideoJob,
        *,
        source_path: str | Path,
        output_dir: str | Path,
        config: AutoTreatmentConfig | None = None,
    ) -> OneButtonTreatmentResult:
        config = config or AutoTreatmentConfig()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        media = self.probe.probe(source_path)
        if not media.has_video:
            raise ValueError("source has no video stream")
        warnings: list[str] = []
        if abs(media.duration_seconds - job.source_duration) > 0.25:
            warnings.append(
                f"manifest/source duration drift: {job.source_duration:.3f}s vs probed {media.duration_seconds:.3f}s; using probe"
            )
        duration = media.duration_seconds

        seam_candidates: list[SeamCandidate] = []
        loop_anchor = config.loop_anchor
        loop_score: float | None = None
        if loop_anchor is None and config.auto_hunt_loop:
            seam_candidates = self.seams.hunt(
                source_path,
                duration_seconds=duration,
                fps=media.fps or 30,
                has_audio=media.has_audio,
                top_n=8,
            )
            retained = retained_segments(
                duration,
                config.remove_ranges,
                head_trim=config.retention_head_trim,
            )
            viable = [
                candidate for candidate in seam_candidates
                if candidate.score >= config.minimum_rotation_score
                and any(seg.source_start <= candidate.anchor_seconds <= seg.source_end for seg in retained)
            ]
            if viable:
                loop_anchor = viable[0].anchor_seconds
                loop_score = viable[0].score
            elif seam_candidates:
                warnings.append("Seam Hunter found candidates, but none survived the retained-footage gate.")
        elif loop_anchor is not None:
            loop_score = 100.0

        plans = build_hypothesis_variants(
            duration,
            remove_ranges=config.remove_ranges,
            compression_remove_ranges=config.compression_remove_ranges,
            retention_head_trim=config.retention_head_trim,
            loop_anchor=loop_anchor,
            loop_score=loop_score,
            payoff_range=config.payoff_range,
            alternate_hook_range=config.alternate_hook_range,
            primary_text=config.primary_text,
            include_no_text_variant=config.include_no_text_variant,
        )

        match_candidates: list[MatchSeamCandidate] = []
        if config.include_match_loop:
            match_candidates = self.seams.hunt_match_pairs(source_path, duration_seconds=duration, top_n=3)
            if match_candidates and match_candidates[0].score >= config.minimum_match_score:
                best_match = match_candidates[0]
                plans["match_loop"] = build_match_loop_plan(
                    best_match.start_seconds, best_match.end_seconds, score=best_match.score
                )

        for plan in plans.values():
            plan.metadata.setdefault("content_class", config.content_class)
            plan.metadata.setdefault("motion_level", config.motion_level)
            if config.hook_type != "unknown":
                plan.metadata.setdefault("hook_type", config.hook_type)
        plan_dir = output_dir / "plans"
        for kind, plan in plans.items():
            dump_plan(plan, plan_dir / f"{kind}.json")

        local_result = self.local.full_treatment(
            source_path=source_path,
            source_duration=duration,
            plans=plans,
            output_dir=output_dir / "renders",
            require_output_qc=True,
        )
        warnings.extend(local_result.warnings)

        fingerprints: dict[str, CreativeFingerprint] = {}
        for kind, ref in local_result.renders.items():
            plan = plans[kind]
            fp = fingerprint_from_plan(
                plan,
                source_duration=duration,
                audio_mode="natural" if ref.has_audio else "silent",
                content_class=config.content_class,
                hook_type=str(plan.metadata.get("hook_type") or config.hook_type),
                motion_level=config.motion_level,
            )
            fingerprints[kind] = fp

        ranking = _rank_variants(local_result, plans)
        recommended = ranking[0][0] if ranking else None
        preview: str | None = None
        if recommended in {"loop", "match_loop"}:
            ref = local_result.renders.get(recommended)
            if ref and Path(ref.path).exists():
                try:
                    preview_path = output_dir / "previews" / f"{recommended}_3cycles.mp4"
                    self.ffmpeg.repeat_video(
                        ref.path,
                        preview_path,
                        cycles=3,
                        duration_seconds=ref.expected_duration,
                        has_audio=ref.has_audio,
                    )
                    preview = str(preview_path)
                except Exception as exc:
                    warnings.append(f"loop preview failed: {exc}")

        social_copy = fallback_social_copy(job.premise, content_class=config.content_class)
        job.metadata["recommended_local_variant"] = recommended
        job.metadata["creative_fingerprints"] = {kind: fp.to_record() for kind, fp in fingerprints.items()}
        job.metadata["analytics_status"] = "performance_pending"
        job.metadata["last_local_treatment_report"] = str(output_dir / "treatment-report.json")
        job.touch()

        report_path = output_dir / "treatment-report.json"
        report = {
            "job_id": job.job_id,
            "media": asdict(media),
            "seam_candidates": [c.to_record() for c in seam_candidates],
            "match_candidates": [c.to_record() for c in match_candidates],
            "renders": {kind: asdict(ref) for kind, ref in local_result.renders.items()},
            "rejected": local_result.rejected,
            "inspections": {kind: inspection.to_record() for kind, inspection in local_result.inspections.items()},
            "fingerprints": {kind: fp.to_record() for kind, fp in fingerprints.items()},
            "ranking": ranking,
            "recommended_variant": recommended,
            "loop_preview": preview,
            "social_copy": social_copy.to_record(),
            "experiment_registration": {
                "status": "performance_pending",
                "variants": list(local_result.renders),
                "fingerprint_ids": {kind: fp.fingerprint_id for kind, fp in fingerprints.items()},
            },
            "warnings": warnings,
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return OneButtonTreatmentResult(
            media=media,
            seam_candidates=seam_candidates,
            match_candidates=match_candidates,
            plans=plans,
            local=local_result,
            fingerprints=fingerprints,
            ranking=ranking,
            recommended_variant=recommended,
            loop_preview=preview,
            social_copy=social_copy,
            report_path=str(report_path),
            warnings=warnings,
        )


def _rank_variants(local: LocalTreatmentResult, plans: dict[str, LocalEditPlan]) -> list[tuple[str, float]]:
    creative_base = {
        "natural": 66.0,
        "retention": 76.0,
        "compression": 74.0,
        "payoff_first": 80.0,
        "alternate_hook": 78.0,
        "minimal_text": 72.0,
        "loop": 78.0,
        "match_loop": 76.0,
    }
    ranked: list[tuple[str, float]] = []
    for kind in local.renders:
        mechanical = local.inspections[kind].score if kind in local.inspections else 85.0
        loop_score = plans[kind].metadata.get("loop_score")
        creative = float(loop_score) if loop_score is not None else creative_base.get(kind, 65.0)
        score = round(0.58 * mechanical + 0.42 * creative, 2)
        ranked.append((kind, score))
    return sorted(ranked, key=lambda item: item[1], reverse=True)
