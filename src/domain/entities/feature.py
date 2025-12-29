from dataclasses import dataclass


@dataclass
class Feature:
    id: int
    name: str
    description: str | None = None
