from time import perf_counter

from app.config import settings
from app.travel_tools.provider_service import run_mock_tool_loop
from app.travel_tools.schemas import TravelPlanRequest, TravelPlanResponse, TravelRecommendationInput


class TravelProviderError(RuntimeError):
    """Raised when a configured LLM provider cannot produce a tool proposal."""


class TravelToolExecutionError(RuntimeError):
    """Raised when an allowed travel tool cannot be executed."""


def create_travel_plan(payload: TravelPlanRequest) -> TravelPlanResponse:
    """Run the safe mock tool loop behind backend A's API contract."""
    selected_provider = payload.provider or settings.llm_provider
    if selected_provider != "mock":
        raise TravelProviderError("현재 여행 Tool Use는 mock Provider만 지원합니다.")
    started = perf_counter()
    request = TravelRecommendationInput.model_validate(payload.model_dump(exclude={"provider"}))
    try:
        tool_calls, tool_results, answer = run_mock_tool_loop(request)
    except Exception as error:
        raise TravelToolExecutionError("여행 추천 Tool 실행에 실패했습니다.") from error
    if not all(result.success for result in tool_results):
        raise TravelToolExecutionError("여행 추천 Tool 실행에 실패했습니다.")
    return TravelPlanResponse(
        provider="mock", model="deterministic-travel-tool-mock", request=request,
        tool_calls=tool_calls, tool_results=tool_results, answer=answer,
        latency_ms=max(0, int((perf_counter() - started) * 1000)),
    )
