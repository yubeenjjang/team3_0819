"""카카오맵 구조화 여행 추천 전용 API Router입니다."""

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.map_travel.provider_service import (
    MapTravelOutputValidationError,
    MapTravelProviderError,
)
from app.map_travel.schemas import MapTravelRequest, MapTravelResponse
from app.map_travel.service import create_map_travel
from app.openapi import UNIT_02_TAG


map_travel_router = APIRouter()


@map_travel_router.post(
    "/api/structured/map-travel",
    response_model=MapTravelResponse,
    tags=[UNIT_02_TAG],
)
def create_map_travel_response(payload: MapTravelRequest) -> MapTravelResponse:
    """검증된 지도 여행 추천을 생성하고 안전한 API 오류로 변환합니다."""

    try:
        return create_map_travel(payload)
    except (MapTravelOutputValidationError, ValidationError) as error:
        raise HTTPException(
            status_code=422,
            detail="Provider의 구조화 결과가 여행 추천 계약에 맞지 않습니다.",
        ) from error
    except MapTravelProviderError as error:
        raise HTTPException(
            status_code=502,
            detail="선택한 Provider의 여행 추천 생성에 실패했습니다.",
        ) from error
