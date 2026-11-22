"""API v1 router."""

from fastapi import APIRouter, Depends

from src.api.dependencies.features import require_feature
from src.api.v1.endpoints import (
    auth,
    brand,
    cities,
    custom_orders,
    customers,
    dealership_media,
    dealership_reviews,
    dealerships,
    favorites,
    features,
    health,
    logs,
    lookups,
    model_media,
    model_vehicles,
    models,
    operations,
    orders,
    reviews,
    testdrives,
    trims,
    users,
    vehicles,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(health.router)
router.include_router(brand.router)
router.include_router(lookups.router)
router.include_router(users.router)
router.include_router(customers.router)
router.include_router(cities.router)
router.include_router(dealerships.router)
router.include_router(dealership_media.router)
router.include_router(dealership_reviews.router, dependencies=[Depends(require_feature("reviews"))])
router.include_router(models.router)
router.include_router(model_media.router)
router.include_router(trims.router)
router.include_router(model_vehicles.router)
router.include_router(features.router)
router.include_router(vehicles.router)
router.include_router(orders.router)
router.include_router(custom_orders.router, dependencies=[Depends(require_feature("custom_orders"))])
router.include_router(reviews.router, dependencies=[Depends(require_feature("reviews"))])
router.include_router(testdrives.router, dependencies=[Depends(require_feature("test_drives"))])
router.include_router(favorites.router, dependencies=[Depends(require_feature("favorites"))])
router.include_router(logs.router)
router.include_router(operations.router)
