"""카카오맵 여행 추천 기능의 애플리케이션 서비스입니다.

Backend A가 제공하는 Schema와 Provider 진입점을 조합해 HTTP 계층에서
사용할 최종 응답을 만듭니다. FastAPI 예외 변환은 Router가 담당합니다.
"""

from app.config import settings
from app.map_travel.provider_service import generate_map_travel
from app.map_travel.schemas import MapTravelRequest, MapTravelResponse


def create_map_travel(payload: MapTravelRequest) -> MapTravelResponse:
    """기본 Provider를 결정하고 검증된 여행 추천 응답을 반환합니다."""

    selected_provider = payload.provider or settings.llm_provider
    result = generate_map_travel(selected_provider, payload.message)

    return MapTravelResponse.model_validate(
        {
            "provider": result.provider,
            "model": result.model,
            "content": result.content,
            "latency_ms": result.latency_ms,
        }
    )
