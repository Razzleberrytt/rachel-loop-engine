from __future__ import annotations

from dataclasses import asdict, dataclass
import re


@dataclass(frozen=True)
class SocialCopy:
    title: str
    hashtags: list[str]

    def to_record(self) -> dict[str, object]:
        return asdict(self)


def fallback_social_copy(premise: str, *, content_class: str = "family") -> SocialCopy:
    """Deterministic fallback; a connected creative model can replace this upstream."""
    clean = re.sub(r"\s+", " ", premise).strip(" .")
    title = clean[:72].rstrip() if clean else "Wait for the reaction"
    if len(clean) > 72:
        title = title.rsplit(" ", 1)[0]
    mapping = {
        "baby_reaction": ["#shorts", "#baby", "#family", "#funny"],
        "family_reaction": ["#shorts", "#family", "#reaction", "#funny"],
        "cute": ["#shorts", "#cute", "#family"],
    }
    hashtags = mapping.get(content_class, ["#shorts", "#family"])
    return SocialCopy(title=title, hashtags=hashtags)
