from abc import ABC, abstractmethod

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


class IUnitOfWork(ABC):
    """Interface for unit of work operations."""

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Enters the async context manager."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exits the async context manager."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commits the current transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rolls back the current transaction."""
        pass

    @property
    @abstractmethod
    def user_repository(self) -> IUserRepository:
        """Returns the user repository."""
        pass

    @property
    @abstractmethod
    def customer_repository(self) -> ICustomerRepository:
        """Returns the customer repository."""
        pass

    @property
    @abstractmethod
    def city_repository(self) -> ICityRepository:
        """Returns the city repository."""
        pass

    @property
    @abstractmethod
    def dealership_repository(self) -> IDealershipRepository:
        """Returns the dealership repository."""
        pass

    @property
    @abstractmethod
    def engine_repository(self) -> IEngineRepository:
        """Returns the engine repository."""
        pass

    @property
    @abstractmethod
    def transmission_repository(self) -> ITransmissionRepository:
        """Returns the transmission repository."""
        pass

    @property
    @abstractmethod
    def model_repository(self) -> IModelRepository:
        """Returns the model repository."""
        pass

    @property
    @abstractmethod
    def model_media_repository(self) -> IModelMediaRepository:
        """Returns the model media repository."""
        pass

    @property
    @abstractmethod
    def feature_repository(self) -> IFeatureRepository:
        """Returns the feature repository."""
        pass

    @property
    @abstractmethod
    def vehicle_repository(self) -> IVehicleRepository:
        """Returns the vehicle repository."""
        pass

    @property
    @abstractmethod
    def order_repository(self) -> IOrderRepository:
        """Returns the order repository."""
        pass

    @property
    @abstractmethod
    def custom_order_repository(self) -> ICustomOrderRepository:
        """Returns the custom order repository."""
        pass

    @property
    @abstractmethod
    def review_repository(self) -> IReviewRepository:
        """Returns the review repository."""
        pass

    @property
    @abstractmethod
    def test_drive_repository(self) -> ITestDriveRepository:
        """Returns the test drive repository."""
        pass

    @property
    @abstractmethod
    def vehicle_media_repository(self) -> IVehicleMediaRepository:
        """Returns the vehicle media repository."""
        pass

    @property
    @abstractmethod
    def favorite_repository(self) -> IFavoriteRepository:
        """Returns the favorite repository."""
        pass
