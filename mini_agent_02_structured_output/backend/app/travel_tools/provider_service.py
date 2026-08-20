from app.travel_tools.executor import execute_tool_call
from app.travel_tools.schemas import ToolCall, ToolExecutionResult, TravelRecommendationInput


def create_mock_tool_calls(request: TravelRecommendationInput) -> list[ToolCall]:
    """Mock Provider가 제안하는 결정적이고 재현 가능한 Tool Call 목록입니다."""
    arguments = request.model_dump(mode="json")
    return [
        ToolCall(id="call_attractions_001", name="recommend_attractions", arguments=arguments),
        ToolCall(id="call_restaurants_001", name="recommend_restaurants", arguments=arguments),
    ]


def run_mock_tool_loop(
    request: TravelRecommendationInput,
) -> tuple[list[ToolCall], list[ToolExecutionResult], str]:
    """Tool Call 제안, 검증된 실행, Tool Result 기반 답변의 Mock 전체 흐름입니다."""
    tool_calls = create_mock_tool_calls(request)
    results = [execute_tool_call(tool_call) for tool_call in tool_calls]
    attraction_count = len(results[0].data.attractions) if results[0].success and results[0].data else 0
    restaurant_count = len(results[1].data.restaurants) if results[1].success and results[1].data else 0
    answer = (
        f"{request.city} {request.guests}명 여행 일정에 맞춰 관광지 {attraction_count}곳과 "
        f"맛집 {restaurant_count}곳을 추천했습니다. 지도에서 위치를 확인하세요."
    )
    return tool_calls, results, answer
