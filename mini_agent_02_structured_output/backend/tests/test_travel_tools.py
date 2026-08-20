from datetime import date

import pytest
from pydantic import ValidationError

from app.travel_tools.executor import ToolNotAllowedError, execute_tool_call
from app.travel_tools.provider_service import run_mock_tool_loop
from app.travel_tools.schemas import ToolCall, TravelRecommendationInput


def make_input() -> TravelRecommendationInput:
    return TravelRecommendationInput(
        city="부산",
        check_in=date(2026, 8, 12),
        check_out=date(2026, 8, 14),
        guests=2,
    )


def test_mock_tool_loop_returns_attractions_and_restaurants() -> None:
    calls, results, answer = run_mock_tool_loop(make_input())

    assert [call.name for call in calls] == ["recommend_attractions", "recommend_restaurants"]
    assert all(result.success for result in results)
    assert results[0].data is not None
    assert results[1].data is not None
    assert "관광지" in answer and "맛집" in answer


def test_executor_rejects_extra_tool_arguments() -> None:
    result = execute_tool_call(
        ToolCall(
            id="call_invalid_001",
            name="recommend_attractions",
            arguments={**make_input().model_dump(mode="json"), "payment": True},
        )
    )

    assert not result.success
    assert result.error_code == "TOOL_VALIDATION_ERROR"


def test_executor_rejects_disallowed_tool_name() -> None:
    class UnsafeToolCall:
        id = "call_unsafe_001"
        name = "delete_database"
        arguments = {}

    with pytest.raises(ToolNotAllowedError):
        execute_tool_call(UnsafeToolCall())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("check_in", "check_out", "guests"),
    [
        (date(2026, 8, 12), date(2026, 8, 12), 2),
        (date(2026, 8, 14), date(2026, 8, 12), 2),
        (date(2026, 8, 12), date(2026, 8, 14), 0),
        (date(2026, 8, 12), date(2026, 8, 14), 11),
    ],
)
def test_tool_input_validates_dates_and_guests(
    check_in: date, check_out: date, guests: int
) -> None:
    with pytest.raises(ValidationError):
        TravelRecommendationInput(
            city="부산", check_in=check_in, check_out=check_out, guests=guests
        )
