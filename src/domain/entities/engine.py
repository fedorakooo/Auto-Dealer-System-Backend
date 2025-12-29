from dataclasses import dataclass

from src.domain.value_objects.fuel_type import FuelType


@dataclass
class Engine:
    id: int
    name: str
    engine_code: str | None = None
    displacement_cm3: int | None = None
    cylinders: int | None = None
    horsepower: int | None = None
    horsepower_electric: int | None = None
    torque_nm: int | None = None
    fuel_type: FuelType = FuelType.GASOLINE
    configuration: str | None = None
    induction: str | None = None
    description: str | None = None
