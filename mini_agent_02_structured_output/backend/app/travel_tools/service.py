from app.travel_tools.schemas import TravelPlanRequest, TravelPlanResponse


class TravelProviderError(RuntimeError):
    """Raised when a configured LLM provider cannot produce a tool proposal."""


class TravelToolExecutionError(RuntimeError):
    """Raised when an allowed travel tool cannot be executed."""


def create_travel_plan(payload: TravelPlanRequest) -> TravelPlanResponse:
    """Service boundary implemented by backend B's provider and tool workflow."""

    del payload
    raise TravelToolExecutionError("여행 Tool 서비스가 아직 연결되지 않았습니다.")
