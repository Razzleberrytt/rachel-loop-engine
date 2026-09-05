from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PromptBook:
    root: Path
    def load(self, name: str) -> str:
        path = self.root / "prompts" / name
        if not path.exists():
            raise FileNotFoundError(path)
        return path.read_text(encoding="utf-8").strip()
    def compose_descript_edit(self, *, variant: str, premise: str, source_duration: float) -> str:
        base = self.load("descript-master-edit.md")
        return f"{base}\n\n## Runtime context\n- variant: {variant}\n- premise: {premise or 'infer from footage'}\n- source_duration_seconds: {source_duration:.3f}\n"
