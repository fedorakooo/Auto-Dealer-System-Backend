import csv
import io
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from src.api.dependencies.services import get_log_service
from src.api.security import get_current_user
from src.application.services.log_service import LogService
from src.domain.entities.user import User

router = APIRouter(prefix="/logs", tags=["Audit Logs"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[dict[str, Any]],
)
async def get_logs(
    log_service: Annotated[LogService, Depends(get_log_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    start_time: datetime | None = Query(None, description="Start time for filtering logs"),
    end_time: datetime | None = Query(None, description="End time for filtering logs"),
    user_id: str | None = Query(None, description="Filter logs by user ID"),
    event_type: str | None = Query(None, description="Filter logs by event type (USER_ACTION, DB_QUERY, ERROR)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
) -> list[dict[str, Any]]:
    """
    Retrieve audit logs.
    Requires authentication.
    """
    return await log_service.search_logs(
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
        event_type=event_type,
        limit=limit,
        skip=skip,
    )


def generate_csv_response(data: list[dict[str, Any]], filename: str) -> StreamingResponse:
    if not data:
        return StreamingResponse(iter(["No data"]), media_type="text/plain")

    output = io.StringIO()
    keys = set()
    for row in data:
        keys.update(row.keys())

    writer = csv.DictWriter(output, fieldnames=list(keys))
    writer.writeheader()
    for row in data:
        writer.writerow({k: str(v) for k, v in row.items()})

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def handle_export(data: list[dict[str, Any]], export_format: str | None, filename: str) -> Any:
    if export_format == "csv":
        return generate_csv_response(data, filename)
    return data


@router.get("/reports/activity", status_code=status.HTTP_200_OK)
async def get_activity_stats(
    log_service: Annotated[LogService, Depends(get_log_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    period: str = Query("day", description="Period: day, week, month"),
    export: str | None = Query(None, description="Export format: csv"),
) -> Any:
    data = await log_service.get_activity_stats(period)
    return handle_export(data, export, "activity_stats.csv")


@router.get("/reports/top-users", status_code=status.HTTP_200_OK)
async def get_top_users(
    log_service: Annotated[LogService, Depends(get_log_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=100),
    export: str | None = Query(None, description="Export format: csv"),
) -> Any:
    data = await log_service.get_top_users(limit)
    return handle_export(data, export, "top_users.csv")


@router.get("/reports/crud-stats", status_code=status.HTTP_200_OK)
async def get_crud_stats(
    log_service: Annotated[LogService, Depends(get_log_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    export: str | None = Query(None, description="Export format: csv"),
) -> Any:
    data = await log_service.get_crud_stats()
    return handle_export(data, export, "crud_stats.csv")


@router.get("/reports/time-series", status_code=status.HTTP_200_OK)
async def get_time_series(
    log_service: Annotated[LogService, Depends(get_log_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    start_time: datetime,
    end_time: datetime,
    interval: str = Query("hour", description="Interval: minute, day, default is hour"),
    export: str | None = Query(None, description="Export format: csv"),
) -> Any:
    data = await log_service.get_time_series(start_time, end_time, interval)
    return handle_export(data, export, "time_series.csv")


@router.get("/reports/anomalies", status_code=status.HTTP_200_OK)
async def detect_anomalies(
    log_service: Annotated[LogService, Depends(get_log_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    threshold_multiplier: float = Query(2.0, ge=1.0),
    export: str | None = Query(None, description="Export format: csv"),
) -> Any:
    data = await log_service.detect_anomalies(threshold_multiplier)
    return handle_export(data, export, "anomalies.csv")
