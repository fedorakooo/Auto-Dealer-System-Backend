from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exception_handlers import exception_container
from src.api.middlewares.audit_log import AuditLogMiddleware
from src.api.v1.router import router as api_v1_router
from src.lifespan import lifespan

app = FastAPI(
    title="Auto Dealer System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuditLogMiddleware)

app.include_router(api_v1_router)

exception_container(app)
