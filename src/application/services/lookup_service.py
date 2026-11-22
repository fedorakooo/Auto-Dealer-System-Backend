from src.application.abstractions.lookup_service import ILookupService
from src.application.dtos.lookup_dto import BodyTypeDTO, EngineLookupDTO, LookupsDTO, TransmissionLookupDTO
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.drive_type import DriveType
from src.domain.value_objects.fuel_type import FuelType
from src.domain.value_objects.transmission_type import TransmissionType


class LookupService(ILookupService):
    """Service for catalog lookups."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def get_lookups(self) -> LookupsDTO:
        """Returns all catalog lookups in one payload."""
        async with self._uow as uow:
            body_types = await uow.body_type_repository.get_all()
            engines = await uow.engine_repository.get_all()
            transmissions = await uow.transmission_repository.get_all()
        return LookupsDTO(
            body_types=[BodyTypeDTO(id=b.id, name=b.name) for b in body_types],
            engines=[
                EngineLookupDTO(id=e.id, name=e.name, fuel_type=str(e.fuel_type), horsepower=e.horsepower)
                for e in engines
            ],
            transmissions=[
                TransmissionLookupDTO(id=t.id, name=t.name, type=str(t.type), number_of_gears=t.number_of_gears)
                for t in transmissions
            ],
            fuel_types=[f.value for f in FuelType],
            transmission_types=[t.value for t in TransmissionType],
            drive_types=[d.value for d in DriveType],
        )
