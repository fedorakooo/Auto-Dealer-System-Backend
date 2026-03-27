import asyncio
import jwt
from typing import Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.api.dependencies.services import get_log_service
from src.infrastructure.mongodb.client import mongodb_client


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)

        method = request.method
        if method in ("POST", "PUT", "DELETE", "PATCH"):
            self._log_action(request, response.status_code)

        return response

    def _log_action(self, request: Request, status_code: int) -> None:
        if mongodb_client.db is None:
            return

        method = request.method
        path = request.url.path

        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")
            except Exception:
                pass

        if "auth/signin" in path or "auth/login" in path:
            action = "LOGIN"
        elif "auth/logout" in path:
            action = "LOGOUT"
        elif "auth/signup" in path:
            action = "SIGNUP"
        elif method == "POST":
            action = f"CREATE_{path.split('/')[-1].upper()}"
        elif method in ("PUT", "PATCH"):
            action = f"UPDATE_{path.split('/')[-1].upper()}"
        elif method == "DELETE":
            action = f"DELETE_{path.split('/')[-1].upper()}"
        else:
            action = f"ACTION_{method}"

        details: dict[str, Any] = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "client_ip": request.client.host if request.client else None,
        }

        try:
            log_service = get_log_service()
            asyncio.create_task(
                log_service.log_user_action(
                    action=action,
                    user_id=str(user_id) if user_id else None,
                    details=details,
                )
            )
        except Exception:
            pass
