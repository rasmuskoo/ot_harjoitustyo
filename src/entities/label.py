"""Label entity."""

from dataclasses import dataclass


@dataclass
class Label:
    """Represents a reusable task label.

    Attributes:
        name: Normalized label name shown to users.
        id: Database id for the label, or None before the label is stored.
    """

    name: str
    id: int | None = None
