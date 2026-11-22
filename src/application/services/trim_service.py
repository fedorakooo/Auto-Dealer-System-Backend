from uuid import UUID

from src.application.abstractions.trim_service import ITrimService
from src.application.dtos.trim_dto import TrimCreateDTO, TrimDTO, TrimUpdateDTO
from src.application.exceptions.errors import BusinessError, NotFoundError, ValidationError
from src.application.mappers.trim_mapper import TrimMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.entities.trim import Trim
from src.domain.exceptions.trim_errors import TrimInUseError


class TrimService(ITrimService):
    """Service for trim operations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def create_trim(self, create_dto: TrimCreateDTO) -> TrimDTO:
        """Create a trim of a model."""
        async with self._uow as uow:
            await self._require_model(uow, create_dto.model_id)
            await self._check_references(uow, create_dto.engine_id, create_dto.transmission_id)
            self._check_weights(create_dto.curb_weight_kg, create_dto.gross_weight_kg)

            trim = TrimMapper.from_create_dto_to_entity(create_dto)
            created_trim = await uow.trim_repository.create(trim)
        return TrimMapper.from_entity_to_dto(created_trim)

    async def get_trim(self, trim_id: UUID) -> TrimDTO:
        """Get trim by ID."""
        async with self._uow as uow:
            trim = await self._require_trim(uow, trim_id)
        return TrimMapper.from_entity_to_dto(trim)

    async def get_trims_by_model(self, model_id: UUID) -> list[TrimDTO]:
        """Get all trims of a model."""
        async with self._uow as uow:
            await self._require_model(uow, model_id)
            trims = await uow.trim_repository.get_by_model_id(model_id)
        return [TrimMapper.from_entity_to_dto(trim) for trim in trims]

    async def update_trim(self, trim_id: UUID, update_dto: TrimUpdateDTO) -> TrimDTO:
        """Update trim."""
        async with self._uow as uow:
            trim = await self._require_trim(uow, trim_id)
            await self._check_references(uow, update_dto.engine_id, update_dto.transmission_id)

            updated_trim = TrimMapper.from_update_dto_to_entity(trim, update_dto)
            self._check_weights(updated_trim.curb_weight_kg, updated_trim.gross_weight_kg)
            saved_trim = await uow.trim_repository.update(updated_trim)
        return TrimMapper.from_entity_to_dto(saved_trim)

    async def delete_trim(self, trim_id: UUID) -> bool:
        """Delete trim; fails while vehicles or custom orders use it."""
        async with self._uow as uow:
            await self._require_trim(uow, trim_id)
            try:
                return await uow.trim_repository.delete(trim_id)
            except TrimInUseError as exc:
                raise BusinessError("Trim is used by vehicles or custom orders and cannot be deleted") from exc

    @staticmethod
    async def _require_model(uow: IUnitOfWork, model_id: UUID) -> None:
        if not await uow.model_repository.get_by_id(model_id):
            raise NotFoundError("Model", str(model_id))

    @staticmethod
    async def _require_trim(uow: IUnitOfWork, trim_id: UUID) -> Trim:
        trim = await uow.trim_repository.get_by_id(trim_id)
        if not trim:
            raise NotFoundError("Trim", str(trim_id))
        return trim

    @staticmethod
    async def _check_references(uow: IUnitOfWork, engine_id: int | None, transmission_id: int | None) -> None:
        if engine_id is not None and not await uow.engine_repository.get_by_id(engine_id):
            raise NotFoundError("Engine", str(engine_id))
        if transmission_id is not None and not await uow.transmission_repository.get_by_id(transmission_id):
            raise NotFoundError("Transmission", str(transmission_id))

    @staticmethod
    def _check_weights(curb_weight_kg: int | None, gross_weight_kg: int | None) -> None:
        if curb_weight_kg is not None and gross_weight_kg is not None and gross_weight_kg < curb_weight_kg:
            raise ValidationError("Gross weight cannot be lower than curb weight")
