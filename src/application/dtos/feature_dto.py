from dataclasses import dataclass


@dataclass
class FeatureCreateDTO:
    name: str
    description: str | None = None


@dataclass
class FeatureUpdateDTO:
    name: str | None = None
    description: str | None = None


@dataclass
class FeatureDTO:
    id: int
    name: str
    description: str | None = None


@dataclass
class FeatureAttachDTO:
    feature_id: int


@dataclass
class FeatureDetachDTO:
    feature_id: int
