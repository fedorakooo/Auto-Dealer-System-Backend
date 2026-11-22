from abc import ABC, abstractmethod
from types import TracebackType

from src.domain.abstractions.database.repositories.city_repository import ICityRepository
from src.domain.abstractions.database.repositories.custom_order_repository import ICustomOrderRepository
from src.domain.abstractions.database.repositories.customer_repository import ICustomerRepository
from src.domain.abstractions.database.repositories.dealership_media_repository import IDealershipMediaRepository
from src.domain.abstractions.database.repositories.dealership_repository import IDealershipRepository
from src.domain.abstractions.database.repositories.dealership_review_repository import IDealershipReviewRepository
from src.domain.abstractions.database.repositories.engine_repository import IEngineRepository
from src.domain.abstractions.database.repositories.favorite_repository import IFavoriteRepository
from src.domain.abstractions.database.repositories.feature_repository import IFeatureRepository
from src.domain.abstractions.database.repositories.model_media_repository import IModelMediaRepository
from src.domain.abstractions.database.repositories.model_repository import IModelRepository
from src.domain.abstractions.database.repositories.operations_repository import IOperationsRepository
from src.domain.abstractions.database.repositories.order_repository import IOrderRepository
from src.domain.abstractions.database.repositories.review_repository import IReviewRepository
from src.domain.abstractions.database.repositories.testdrive_repository import ITestDriveRepository
from src.domain.abstractions.database.repositories.transmission_repository import ITransmissionRepository
from src.domain.abstractions.database.repositories.trim_repository import ITrimRepository
from src.domain.abstractions.database.repositories.user_repository import IUserRepository
from src.domain.abstractions.database.repositories.vehicle_media_repository import IVehicleMediaRepository
from src.domain.abstractions.database.repositories.vehicle_repository import IVehicleRepository


class IUnitOfWork(ABC):
    """Interface for unit of work operations."""

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Enters the async context manager."""

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Exits the async context manager."""

    @abstractmethod
    async def commit(self) -> None:
        """Commits the current transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back the current transaction."""

    @property
    @abstractmethod
    def user_repository(self) -> IUserRepository:
        """Returns the user repository."""

    @property
    @abstractmethod
    def customer_repository(self) -> ICustomerRepository:
        """Returns the customer repository."""

    @property
    @abstractmethod
    def city_repository(self) -> ICityRepository:
        """Returns the city repository."""

    @property
    @abstractmethod
    def dealership_repository(self) -> IDealershipRepository:
        """Returns the dealership repository."""

    @property
    @abstractmethod
    def dealership_media_repository(self) -> IDealershipMediaRepository:
        """Returns the dealership media repository."""

    @property
    @abstractmethod
    def dealership_review_repository(self) -> IDealershipReviewRepository:
        """Returns the dealership review repository."""


    @property
    @abstractmethod
    def engine_repository(self) -> IEngineRepository:
        """Returns the engine repository."""

    @property
    @abstractmethod
    def transmission_repository(self) -> ITransmissionRepository:
        """Returns the transmission repository."""

    @property
    @abstractmethod
    def model_repository(self) -> IModelRepository:
        """Returns the model repository."""

    @property
    @abstractmethod
    def model_media_repository(self) -> IModelMediaRepository:
        """Returns the model media repository."""

    @property
    @abstractmethod
    def trim_repository(self) -> ITrimRepository:
        """Returns the trim repository."""

    @property
    @abstractmethod
    def feature_repository(self) -> IFeatureRepository:
        """Returns the feature repository."""

    @property
    @abstractmethod
    def vehicle_repository(self) -> IVehicleRepository:
        """Returns the vehicle repository."""

    @property
    @abstractmethod
    def order_repository(self) -> IOrderRepository:
        """Returns the order repository."""

    @property
    @abstractmethod
    def custom_order_repository(self) -> ICustomOrderRepository:
        """Returns the custom order repository."""

    @property
    @abstractmethod
    def review_repository(self) -> IReviewRepository:
        """Returns the review repository."""

    @property
    @abstractmethod
    def test_drive_repository(self) -> ITestDriveRepository:
        """Returns the test drive repository."""

    @property
    @abstractmethod
    def vehicle_media_repository(self) -> IVehicleMediaRepository:
        """Returns the vehicle media repository."""

    @property
    @abstractmethod
    def favorite_repository(self) -> IFavoriteRepository:
        """Returns the favorite repository."""

    @property
    @abstractmethod
    def operations_repository(self) -> IOperationsRepository:
        """Returns the repository for extended database operations."""
