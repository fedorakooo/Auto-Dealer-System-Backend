from uuid import UUID

from src.application.abstractions.model_service import IModelService
from src.application.dtos.model_dto import ModelCreateDTO, ModelDTO, ModelUpdateDTO
from src.application.exceptions.errors import NotFoundError, ValidationError
from src.application.mappers.model_mapper import ModelMapper
from src.domain.abstractions.database.uow import IUnitOfWork
from src.domain.value_objects.filters import ModelFilter


class ModelService(IModelService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create_model(self, create_dto: ModelCreateDTO) -> ModelDTO:
        async with self._uow as uow:
            engine = await uow.engine_repository.get_by_id(create_dto.engine_id)
            if not engine:
                raise NotFoundError("Engine", str(create_dto.engine_id))

            transmission = await uow.transmission_repository.get_by_id(create_dto.transmission_id)
            if not transmission:
                raise NotFoundError("Transmission", str(create_dto.transmission_id))

            if create_dto.production_year_end and create_dto.production_year_start > create_dto.production_year_end:
                raise ValidationError("Production year start must be before or equal to production year end")

            model = ModelMapper.from_create_dto_to_entity(create_dto)
            created_model = await uow.model_repository.create(model)

        return ModelMapper.from_entity_to_dto(created_model)

    async def get_model(self, model_id: UUID) -> ModelDTO:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))
        return ModelMapper.from_entity_to_dto(model)

    async def get_models(self, model_filter: ModelFilter) -> tuple[list[ModelDTO], int]:
        async with self._uow as uow:
            models, total = await uow.model_repository.get_models(model_filter)
        return [ModelMapper.from_entity_to_dto(model) for model in models], total

    async def update_model(self, model_id: UUID, update_dto: ModelUpdateDTO) -> ModelDTO:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            if update_dto.engine_id:
                engine = await uow.engine_repository.get_by_id(update_dto.engine_id)
                if not engine:
                    raise NotFoundError("Engine", str(update_dto.engine_id))

            if update_dto.transmission_id:
                transmission = await uow.transmission_repository.get_by_id(update_dto.transmission_id)
                if not transmission:
                    raise NotFoundError("Transmission", str(update_dto.transmission_id))

            production_year_start = (
                update_dto.production_year_start
                if update_dto.production_year_start is not None
                else model.production_year_start
            )
            production_year_end = (
                update_dto.production_year_end
                if update_dto.production_year_end is not None
                else model.production_year_end
            )
            if production_year_end and production_year_start > production_year_end:
                raise ValidationError("Production year start must be before or equal to production year end")

            updated_model = ModelMapper.from_update_dto_to_entity(model, update_dto)
            saved_model = await uow.model_repository.update(updated_model)

        return ModelMapper.from_entity_to_dto(saved_model)

    async def delete_model(self, model_id: UUID) -> bool:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            result = await uow.model_repository.delete(model_id)
        return result
