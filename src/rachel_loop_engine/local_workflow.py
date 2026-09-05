from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from .adapters.ffmpeg import FfmpegAdapter, LocalRenderRef
from .edl import LocalEditPlan
from .render_qc import RenderInspection, RenderInspector


@dataclass
class LocalTreatmentResult:
    renders: dict[str, LocalRenderRef] = field(default_factory=dict)
    rejected: dict[str, str] = field(default_factory=dict)
    inspections: dict[str, RenderInspection] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class LocalWorkflowRunner:
    """Default execution path: EDL -> deterministic FFmpeg render -> mechanical QC."""

    def __init__(
        self,
        adapter: FfmpegAdapter | None = None,
        inspector: RenderInspector | None = None,
    ) -> None:
        self.adapter = adapter or FfmpegAdapter()
        self.inspector = inspector or RenderInspector()

    def full_treatment(
        self,
        *,
        source_path: str | Path,
        source_duration: float,
        plans: Mapping[str, LocalEditPlan],
        output_dir: str | Path,
        preset: str = "veryfast",
        crf: int = 18,
        require_output_qc: bool = False,
    ) -> LocalTreatmentResult:
        result = LocalTreatmentResult()
        output_dir = Path(output_dir)
        for kind, plan in plans.items():
            try:
                plan.validate(source_duration)
                if kind == "loop" and plan.loop_anchor is not None and not plan.loop_seam_is_source_contiguous():
                    raise ValueError("loop plan failed source-contiguous seam gate")
                ref = self.adapter.render(
                    source_path, output_dir / plan.output_name, plan,
                    source_duration=source_duration, preset=preset, crf=crf,
                )
                rendered_path = Path(ref.path)
                if rendered_path.exists():
                    inspection = self.inspector.inspect(
                        rendered_path,
                        expected_duration=ref.expected_duration,
                        expected_width=plan.width,
                        expected_height=plan.height,
                        expected_fps=plan.fps,
                        expected_audio=ref.has_audio,
                    )
                    result.inspections[kind] = inspection
                    result.warnings.extend(f"{kind}: {warning}" for warning in inspection.warnings)
                    if not inspection.passed:
                        result.rejected[kind] = "; ".join(inspection.failures) or "mechanical QC failed"
                        continue
                elif require_output_qc:
                    result.rejected[kind] = "render output missing; mechanical QC could not run"
                    continue
                result.renders[kind] = ref
            except Exception as exc:
                result.rejected[kind] = str(exc)
        if not result.renders:
            result.warnings.append("No local variant rendered successfully.")
        return result
