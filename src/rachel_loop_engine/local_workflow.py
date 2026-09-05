from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from .adapters.ffmpeg import FfmpegAdapter, LocalRenderRef
from .edl import LocalEditPlan


@dataclass
class LocalTreatmentResult:
    renders: dict[str, LocalRenderRef] = field(default_factory=dict)
    rejected: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class LocalWorkflowRunner:
    """Default execution path: EDL -> deterministic FFmpeg render.

    No editor AI credits are required. AI services can be used upstream to
    suggest timestamps, but rendering and rerendering are deterministic.
    """

    def __init__(self, adapter: FfmpegAdapter | None = None) -> None:
        self.adapter = adapter or FfmpegAdapter()

    def full_treatment(
        self,
        *,
        source_path: str | Path,
        source_duration: float,
        plans: Mapping[str, LocalEditPlan],
        output_dir: str | Path,
        preset: str = "veryfast",
        crf: int = 18,
    ) -> LocalTreatmentResult:
        result = LocalTreatmentResult()
        output_dir = Path(output_dir)

        for kind, plan in plans.items():
            try:
                plan.validate(source_duration)
                if kind == "loop" and plan.loop_anchor is not None and not plan.loop_seam_is_source_contiguous():
                    raise ValueError("loop plan failed source-contiguous seam gate")
                ref = self.adapter.render(
                    source_path,
                    output_dir / plan.output_name,
                    plan,
                    source_duration=source_duration,
                    preset=preset,
                    crf=crf,
                )
                result.renders[kind] = ref
            except Exception as exc:
                result.rejected[kind] = str(exc)

        if not result.renders:
            result.warnings.append("No local variant rendered successfully.")
        return result
