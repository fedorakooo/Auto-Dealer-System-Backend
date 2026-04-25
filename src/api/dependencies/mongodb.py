from fastapi import Request

from src.infrastructure.mongodb.client import MongoDBClient, get_mongodb_client_singleton


def get_mongodb_client(request: Request | None = None) -> MongoDBClient:
    """
    DI provider for MongoDB client.

    - When called by FastAPI, `request` will be injected automatically and we prefer `app.state.mongodb_client`.
    - When used outside request context (startup, background tasks, infra logging), falls back to a singleton.
    """
    if request is not None:
        client: MongoDBClient | None = getattr(request.app.state, "mongodb_client", None)
        if client is not None:
            return client

    return get_mongodb_client_singleton()
