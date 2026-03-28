from fastapi import Request

from src.domain.abstractions.pubsub.manager import IPubSubManager
from src.logger import get_logger

logger = get_logger(__name__)


def get_pubsub_manager(request: Request) -> IPubSubManager:
    pubsub_manager: IPubSubManager | None = request.app.state.pubsub_manager
    if pubsub_manager is None:
        logger.error("Pub/Sub manager is not initialized")
        raise RuntimeError("Pub/Sub manager is not initialized")
    return pubsub_manager
