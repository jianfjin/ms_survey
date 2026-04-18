"""Canonical option profiles for benchmark-sensitive questions."""

from __future__ import annotations

from dataclasses import dataclass
import re


_SPACE_RE = re.compile(r"\s+")


def _normalize_key(value: str) -> str:
    normalized = _SPACE_RE.sub(" ", value.strip().lower())
    return normalized


@dataclass(frozen=True)
class CanonicalOptionProfile:
    """Canonical answer profile for questions requiring stable buckets."""

    canonical_order: tuple[str, ...]
    alias_map: dict[str, str]
    other_label: str = "Other"

    def canonicalize(self, value: str) -> str:
        key = _normalize_key(value)
        if key in self.alias_map:
            return self.alias_map[key]
        return self.other_label


def _build_q004_profile() -> CanonicalOptionProfile:
    canonical_order = (
        "Research data",
        "Registry data",
        "Biobank data",
        "Imaging data",
        "Clinical data",
        "Genetic data",
        "Other",
    )

    aliases = {
        "research data": "Research data",
        "research data (data collected for the purpose of scientific research)": "Research data",
        "registry data": "Registry data",
        "biobank data": "Biobank data",
        "imaging data": "Imaging data",
        "clinical data": "Clinical data",
        "clinical data (data collected for healthcare purposes)": "Clinical data",
        "genetic data": "Genetic data",
        "other": "Other",
        "muu": "Other",
    }

    return CanonicalOptionProfile(
        canonical_order=canonical_order,
        alias_map={_normalize_key(k): v for k, v in aliases.items()},
        other_label="Other",
    )


_PROFILES: dict[str, CanonicalOptionProfile] = {
    "q_004": _build_q004_profile(),
}


def get_option_profile(question_id: str) -> CanonicalOptionProfile | None:
    """Return canonical option profile for a question if configured."""
    return _PROFILES.get(question_id)

