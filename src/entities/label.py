"""Label entity."""

from dataclasses import dataclass


@dataclass
class Label:
    """Represents a reusable task label."""

    name: str
    id: int | None = None
