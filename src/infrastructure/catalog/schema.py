"""Validated shape of a brand catalog pack (catalog.yaml)."""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from src.domain.value_objects.drive_type import DriveType
from src.domain.value_objects.fuel_type import FuelType
from src.domain.value_objects.transmission_type import TransmissionType


class _Item(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CityItem(_Item):
    """City of the catalog pack."""

    name: str = Field(min_length=1, max_length=255)
    country: str = Field(min_length=1, max_length=255)


class DealershipItem(_Item):
    """Dealership of the catalog pack."""

    name: str = Field(min_length=1, max_length=255)
    city: str
    country: str
    address: str = Field(min_length=1, max_length=512)
    phone_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    opening_hours: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    description: str | None = None


class EngineItem(_Item):
    """Engine of the catalog pack."""

    name: str = Field(min_length=1, max_length=255)
    engine_code: str | None = Field(default=None, max_length=100)
    displacement_cm3: int | None = Field(default=None, gt=0)
    cylinders: int | None = Field(default=None, gt=0)
    horsepower: int | None = Field(default=None, gt=0)
    horsepower_electric: int | None = Field(default=None, gt=0)
    torque_nm: int | None = Field(default=None, gt=0)
    fuel_type: FuelType
    configuration: str | None = None
    induction: str | None = None


class TransmissionItem(_Item):
    """Transmission of the catalog pack."""

    name: str = Field(min_length=1, max_length=255)
    type: TransmissionType
    number_of_gears: int = Field(gt=0)


class FeatureItem(_Item):
    """Feature of the catalog pack."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class TrimItem(_Item):
    """Trim of a model in the catalog pack."""

    name: str = Field(min_length=1, max_length=100)
    engine: str
    transmission: str
    drive_type: DriveType | None = None
    max_speed_kmh: int | None = Field(default=None, gt=0)
    acceleration_0_100_sec: Decimal | None = Field(default=None, gt=0, max_digits=3, decimal_places=1)


class ModelItem(_Item):
    """Vehicle model of the catalog pack."""

    name: str = Field(min_length=1, max_length=100)
    body_type: str
    model_code: str | None = Field(default=None, max_length=100)
    is_in_production: bool = True
    production_year_start: int = Field(ge=1900, le=2100)
    number_of_seats: int | None = Field(default=None, gt=0)
    description: str | None = None
    features: list[str] = Field(default_factory=list)
    trims: list[TrimItem] = Field(min_length=1)


class VehicleItem(_Item):
    """Vehicle of the catalog pack."""

    vin: str = Field(pattern=r"^[A-HJ-NPR-Z0-9]{17}$")
    model: str
    trim: str
    dealership: str
    production_year: int = Field(ge=1900, le=2100)
    exterior_color: str = Field(min_length=1, max_length=50)
    interior_color: str | None = Field(default=None, max_length=50)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class CatalogPack(_Item):
    """Whole catalog of one brand; names are the natural keys used for cross-references and upserts."""

    cities: list[CityItem] = Field(default_factory=list)
    dealerships: list[DealershipItem] = Field(default_factory=list)
    body_types: list[str] = Field(default_factory=list)
    engines: list[EngineItem] = Field(default_factory=list)
    transmissions: list[TransmissionItem] = Field(default_factory=list)
    features: list[FeatureItem] = Field(default_factory=list)
    models: list[ModelItem] = Field(default_factory=list)
    vehicles: list[VehicleItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_references(self) -> Self:
        """Ensures every name reference points to an item of the pack."""
        errors: list[str] = []
        cities = {(c.name, c.country) for c in self.cities}
        for d in self.dealerships:
            if (d.city, d.country) not in cities:
                errors.append(f"dealership [{d.name}]: unknown city [{d.city}, {d.country}]")
        engines = {e.name for e in self.engines}
        transmissions = {t.name for t in self.transmissions}
        features = {f.name for f in self.features}
        body_types = set(self.body_types)
        trims: dict[str, set[str]] = {}
        for m in self.models:
            if m.body_type not in body_types:
                errors.append(f"model [{m.name}]: unknown body type [{m.body_type}]")
            errors += [f"model [{m.name}]: unknown feature [{f}]" for f in m.features if f not in features]
            for t in m.trims:
                if t.engine not in engines:
                    errors.append(f"trim [{m.name} {t.name}]: unknown engine [{t.engine}]")
                if t.transmission not in transmissions:
                    errors.append(f"trim [{m.name} {t.name}]: unknown transmission [{t.transmission}]")
            trims[m.name] = {t.name for t in m.trims}
        if len(trims) != len(self.models):
            errors.append("model names must be unique within a pack")
        dealerships = {d.name for d in self.dealerships}
        for v in self.vehicles:
            if v.trim not in trims.get(v.model, set()):
                errors.append(f"vehicle [{v.vin}]: unknown model/trim [{v.model} / {v.trim}]")
            if v.dealership not in dealerships:
                errors.append(f"vehicle [{v.vin}]: unknown dealership [{v.dealership}]")
        if errors:
            raise ValueError("; ".join(errors))
        return self
