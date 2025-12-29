from uuid import UUID

from src.application.abstractions.feature_service import IFeatureService
from src.application.dtos.feature_dto import (
    FeatureAttachDTO,
    FeatureCreateDTO,
    FeatureDetachDTO,
    FeatureDTO,
    FeatureUpdateDTO,
)
from src.application.exceptions.errors import BusinessError, NotFoundError
from src.application.mappers.feature_mapper import FeatureMapper
from src.domain.abstractions.database.uow import IUnitOfWork


class FeatureService(IFeatureService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create_feature(self, create_dto: FeatureCreateDTO) -> FeatureDTO:
        async with self._uow as uow:
            all_features = await uow.feature_repository.get_all()
            next_id = max([f.id for f in all_features], default=0) + 1

            feature = FeatureMapper.from_create_dto_to_entity(create_dto, next_id)
            created_feature = await uow.feature_repository.create(feature)

        return FeatureMapper.from_entity_to_dto(created_feature)

    async def get_feature(self, feature_id: int) -> FeatureDTO:
        async with self._uow as uow:
            feature = await uow.feature_repository.get_by_id(feature_id)
            if not feature:
                raise NotFoundError("Feature", str(feature_id))
        return FeatureMapper.from_entity_to_dto(feature)

    async def get_all_features(self) -> list[FeatureDTO]:
        async with self._uow as uow:
            features = await uow.feature_repository.get_all()
        return [FeatureMapper.from_entity_to_dto(feature) for feature in features]

    async def get_features_by_model(self, model_id: UUID) -> list[FeatureDTO]:
        async with self._uow as uow:
            features = await uow.feature_repository.get_by_model_id(model_id)
        return [FeatureMapper.from_entity_to_dto(feature) for feature in features]

    async def get_features_by_custom_order(self, custom_order_id: UUID) -> list[FeatureDTO]:
        async with self._uow as uow:
            features = await uow.feature_repository.get_by_custom_order_id(custom_order_id)
        return [FeatureMapper.from_entity_to_dto(feature) for feature in features]

    async def update_feature(self, feature_id: int, update_dto: FeatureUpdateDTO) -> FeatureDTO:
        async with self._uow as uow:
            feature = await uow.feature_repository.get_by_id(feature_id)
            if not feature:
                raise NotFoundError("Feature", str(feature_id))

            updated_feature = FeatureMapper.from_update_dto_to_entity(feature, update_dto)
            saved_feature = await uow.feature_repository.update(updated_feature)

        return FeatureMapper.from_entity_to_dto(saved_feature)

    async def delete_feature(self, feature_id: int) -> bool:
        async with self._uow as uow:
            feature = await uow.feature_repository.get_by_id(feature_id)
            if not feature:
                raise NotFoundError("Feature", str(feature_id))

            result = await uow.feature_repository.delete(feature_id)
        return result

    async def attach_feature_to_model(self, model_id: UUID, attach_dto: FeatureAttachDTO) -> bool:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            feature = await uow.feature_repository.get_by_id(attach_dto.feature_id)
            if not feature:
                raise NotFoundError("Feature", str(attach_dto.feature_id))

            model_features = await uow.feature_repository.get_by_model_id(model_id)
            if any(f.id == attach_dto.feature_id for f in model_features):
                raise BusinessError("Feature is already attached to this model")

            result = await uow.feature_repository.add_to_model(model_id, attach_dto.feature_id)
        return result

    async def detach_feature_from_model(self, model_id: UUID, detach_dto: FeatureDetachDTO) -> bool:
        async with self._uow as uow:
            model = await uow.model_repository.get_by_id(model_id)
            if not model:
                raise NotFoundError("Model", str(model_id))

            feature = await uow.feature_repository.get_by_id(detach_dto.feature_id)
            if not feature:
                raise NotFoundError("Feature", str(detach_dto.feature_id))

            result = await uow.feature_repository.remove_from_model(model_id, detach_dto.feature_id)
        return result

    async def attach_feature_to_custom_order(self, custom_order_id: UUID, attach_dto: FeatureAttachDTO) -> bool:
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))

            feature = await uow.feature_repository.get_by_id(attach_dto.feature_id)
            if not feature:
                raise NotFoundError("Feature", str(attach_dto.feature_id))

            order_features = await uow.feature_repository.get_by_custom_order_id(custom_order_id)
            if any(f.id == attach_dto.feature_id for f in order_features):
                raise BusinessError("Feature is already attached to this custom order")

            result = await uow.feature_repository.add_to_custom_order(custom_order_id, attach_dto.feature_id)
        return result

    async def detach_feature_from_custom_order(self, custom_order_id: UUID, detach_dto: FeatureDetachDTO) -> bool:
        async with self._uow as uow:
            custom_order = await uow.custom_order_repository.get_by_id(custom_order_id)
            if not custom_order:
                raise NotFoundError("CustomOrder", str(custom_order_id))

            feature = await uow.feature_repository.get_by_id(detach_dto.feature_id)
            if not feature:
                raise NotFoundError("Feature", str(detach_dto.feature_id))

            result = await uow.feature_repository.remove_from_custom_order(custom_order_id, detach_dto.feature_id)
        return result
