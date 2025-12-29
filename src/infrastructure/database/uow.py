import asyncpg

from src.domain.abstractions.database.connection import IDatabaseConnection
from src.domain.abstractions.database.repositories.city_repository import ICityRepository
from src.domain.abstractions.database.repositories.custom_order_repository import ICustomOrderRepository
from src.domain.abstractions.database.repositories.customer_repository import ICustomerRepository
from src.domain.abstractions.database.repositories.dealership_repository import IDealershipRepository
from src.domain.abstractions.database.repositories.engine_repository import IEngineRepository
from src.domain.abstractions.database.repositories.favorite_repository import IFavoriteRepository
from src.domain.abstractions.database.repositories.feature_repository import IFeatureRepository
from src.domain.abstractions.database.repositories.model_media_repository import IModelMediaRepository
from src.domain.abstractions.database.repositories.model_repository import IModelRepository
from src.domain.abstractions.database.repositories.order_repository import IOrderRepository
from src.domain.abstractions.database.repositories.review_repository import IReviewRepository
from src.domain.abstractions.database.repositories.testdrive_repository import ITestDriveRepository
from src.domain.abstractions.database.repositories.transmission_repository import ITransmissionRepository
from src.domain.abstractions.database.repositories.user_repository import IUserRepository
from src.domain.abstractions.database.repositories.vehicle_media_repository import IVehicleMediaRepository
from src.domain.abstractions.database.repositories.vehicle_repository import IVehicleRepository
from src.domain.abstractions.database.uow import IUnitOfWork
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.database.exceptions import DatabaseTransactionError, UnitOfWorkNotStartedError
from src.infrastructure.database.repositories.city_repository import CityRepository
from src.infrastructure.database.repositories.custom_order_repository import CustomOrderRepository
from src.infrastructure.database.repositories.customer_repository import CustomerRepository
from src.infrastructure.database.repositories.dealership_repository import DealershipRepository
from src.infrastructure.database.repositories.engine_repository import EngineRepository
from src.infrastructure.database.repositories.favorite_repository import FavoriteRepository
from src.infrastructure.database.repositories.feature_repository import FeatureRepository
from src.infrastructure.database.repositories.model_media_repository import ModelMediaRepository
from src.infrastructure.database.repositories.model_repository import ModelRepository
from src.infrastructure.database.repositories.order_repository import OrderRepository
from src.infrastructure.database.repositories.review_repository import ReviewRepository
from src.infrastructure.database.repositories.test_drive_repository import TestDriveRepository
from src.infrastructure.database.repositories.transmission_repository import TransmissionRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.vehicle_media_repository import VehicleMediaRepository
from src.infrastructure.database.repositories.vehicle_repository import VehicleRepository
from src.logger import get_logger

logger = get_logger(__name__)


class UnitOfWork(IUnitOfWork):
    def __init__(self, db_connection: IDatabaseConnection):
        self._db = db_connection
        self._connection: asyncpg.Connection | None = None
        self._transaction: asyncpg.transactions.Transaction | None = None
        self._transactional_db: IDatabaseConnection | None = None
        self._user_repository: IUserRepository | None = None
        self._customer_repository: ICustomerRepository | None = None
        self._city_repository: ICityRepository | None = None
        self._dealership_repository: IDealershipRepository | None = None
        self._engine_repository: IEngineRepository | None = None
        self._transmission_repository: ITransmissionRepository | None = None
        self._model_repository: IModelRepository | None = None
        self._model_media_repository: IModelMediaRepository | None = None
        self._feature_repository: IFeatureRepository | None = None
        self._vehicle_repository: IVehicleRepository | None = None
        self._order_repository: IOrderRepository | None = None
        self._custom_order_repository: ICustomOrderRepository | None = None
        self._review_repository: IReviewRepository | None = None
        self._test_drive_repository: ITestDriveRepository | None = None
        self._vehicle_media_repository: IVehicleMediaRepository | None = None
        self._favorite_repository: IFavoriteRepository | None = None

    async def __aenter__(self) -> "UnitOfWork":
        logger.debug("Starting database transaction")
        self._connection = await self._db.acquire()
        self._transaction = self._connection.transaction()
        await self._transaction.start()

        self._transactional_db = DatabaseConnection(self._connection)

        self._user_repository = UserRepository(self._transactional_db)
        self._customer_repository = CustomerRepository(self._transactional_db)
        self._city_repository = CityRepository(self._transactional_db)
        self._dealership_repository = DealershipRepository(self._transactional_db)
        self._engine_repository = EngineRepository(self._transactional_db)
        self._transmission_repository = TransmissionRepository(self._transactional_db)
        self._model_repository = ModelRepository(self._transactional_db)
        self._model_media_repository = ModelMediaRepository(self._transactional_db)
        self._feature_repository = FeatureRepository(self._transactional_db)
        self._vehicle_repository = VehicleRepository(self._transactional_db)
        self._order_repository = OrderRepository(self._transactional_db)
        self._custom_order_repository = CustomOrderRepository(self._transactional_db)
        self._review_repository = ReviewRepository(self._transactional_db)
        self._test_drive_repository = TestDriveRepository(self._transactional_db)
        self._vehicle_media_repository = VehicleMediaRepository(self._transactional_db)
        self._favorite_repository = FavoriteRepository(self._transactional_db)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.debug(f"Transaction rollback due to exception: {exc_type.__name__}")
            await self.rollback()
        else:
            await self.commit()

        if self._connection:
            await self._db.release(self._connection)
            self._connection = None
            self._transaction = None
            logger.debug("Database connection released")

    async def commit(self) -> None:
        if not self._transaction:
            raise DatabaseTransactionError("Transaction is not started")
        try:
            logger.debug("Committing database transaction")
            await self._transaction.commit()
            logger.debug("Database transaction committed successfully")
        except Exception as exc:
            logger.error(f"Failed to commit transaction: {exc}", exc_info=True)
            raise DatabaseTransactionError(f"Failed to commit transaction: {exc}") from exc

    async def rollback(self) -> None:
        if not self._transaction:
            raise DatabaseTransactionError("Transaction is not started")
        try:
            logger.debug("Rolling back database transaction")
            await self._transaction.rollback()
            logger.debug("Database transaction rolled back successfully")
        except Exception as exc:
            logger.error(f"Failed to rollback transaction: {exc}", exc_info=True)
            raise DatabaseTransactionError(f"Failed to rollback transaction: {exc}") from exc

    @property
    def user_repository(self) -> IUserRepository:
        if self._user_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._user_repository

    @property
    def customer_repository(self) -> ICustomerRepository:
        if self._customer_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._customer_repository

    @property
    def city_repository(self) -> ICityRepository:
        if self._city_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._city_repository

    @property
    def dealership_repository(self) -> IDealershipRepository:
        if self._dealership_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._dealership_repository

    @property
    def engine_repository(self) -> IEngineRepository:
        if self._engine_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._engine_repository

    @property
    def transmission_repository(self) -> ITransmissionRepository:
        if self._transmission_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._transmission_repository

    @property
    def model_repository(self) -> IModelRepository:
        if self._model_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._model_repository

    @property
    def model_media_repository(self) -> IModelMediaRepository:
        if self._model_media_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._model_media_repository

    @property
    def feature_repository(self) -> IFeatureRepository:
        if self._feature_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._feature_repository

    @property
    def vehicle_repository(self) -> IVehicleRepository:
        if self._vehicle_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._vehicle_repository

    @property
    def order_repository(self) -> IOrderRepository:
        if self._order_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._order_repository

    @property
    def custom_order_repository(self) -> ICustomOrderRepository:
        if self._custom_order_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._custom_order_repository

    @property
    def review_repository(self) -> IReviewRepository:
        if self._review_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._review_repository

    @property
    def test_drive_repository(self) -> ITestDriveRepository:
        if self._test_drive_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._test_drive_repository

    @property
    def vehicle_media_repository(self) -> IVehicleMediaRepository:
        if self._vehicle_media_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._vehicle_media_repository

    @property
    def favorite_repository(self) -> IFavoriteRepository:
        if self._favorite_repository is None:
            raise UnitOfWorkNotStartedError()
        return self._favorite_repository
