from datetime import date
from typing import Any

from core.api_client import request


def generate_travel_plan(
    provider: str,
    city: str,
    check_in: date,
    check_out: date,
    guests: int,
) -> dict[str, Any]:
    """Request the 2-5 travel Tool Use API using the shared contract."""
    return request(
        "POST",
        "/api/tools/travel-plan",
        json={
            "provider": provider,
            "city": city,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests,
        },
    )
