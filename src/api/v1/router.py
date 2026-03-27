"""API v1 router."""

from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth,
    cities,
    custom_orders,
    customers,
    dealerships,
    favorites,
    features,
    health,
    models,
    orders,
    reviews,
    testdrives,
    users,
    vehicles,
    logs,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(health.router)
router.include_router(users.router)
router.include_router(customers.router)
router.include_router(cities.router)
router.include_router(dealerships.router)
router.include_router(models.router)
router.include_router(features.router)
router.include_router(vehicles.router)
router.include_router(orders.router)
router.include_router(custom_orders.router)
router.include_router(reviews.router)
router.include_router(testdrives.router)
router.include_router(favorites.router)
router.include_router(logs.router)
