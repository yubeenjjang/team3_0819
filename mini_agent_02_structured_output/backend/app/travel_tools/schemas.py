from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


TravelCity = Literal["서울", "부산", "제주", "강릉", "인천", "대전", "대구", "광주", "전주", "경주"]
TravelToolName = Literal["recommend_attractions", "recommend_restaurants"]


class TravelRecommendationInput(BaseModel):
    """두 여행 조회 Tool이 공유하는 검증된 입력값입니다."""

    model_config = ConfigDict(extra="forbid")

    city: TravelCity = Field(description="여행 지역")
    check_in: date = Field(description="여행 일정 시작일")
    check_out: date = Field(description="여행 일정 종료일")
    guests: int = Field(ge=1, le=10, description="여행 인원")

    @model_validator(mode="after")
    def validate_travel_dates(self) -> "TravelRecommendationInput":
        if self.check_out <= self.check_in:
            raise ValueError("여행 일정 종료일은 시작일 이후여야 합니다.")
        return self


class Attraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    category: str = Field(min_length=1, max_length=50)


class Restaurant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    estimated_price_krw: int = Field(ge=0, description="예상 1인 가격(원)")


class AttractionRecommendationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: TravelCity = Field(description="조회 지역")
    attractions: list[Attraction] = Field(min_length=1, max_length=10)
    source: Literal["mock"] = Field(description="조회 데이터 출처")


class RestaurantRecommendationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: TravelCity = Field(description="조회 지역")
    restaurants: list[Restaurant] = Field(min_length=1, max_length=10)
    source: Literal["mock"] = Field(description="조회 데이터 출처")


class ToolCall(BaseModel):
    """Provider가 제안한 Tool Call입니다. 실행 전 반드시 ToolExecutor를 거칩니다."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=100)
    name: TravelToolName = Field(description="Allowlist에 등록된 Tool 이름")
    arguments: dict[str, Any] = Field(description="Provider가 제안한 Tool 인자")


class ToolExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_call_id: str = Field(min_length=1, max_length=100)
    name: TravelToolName = Field(description="실행한 Tool 이름")
    success: bool = Field(description="Tool 실행 성공 여부")
    data: AttractionRecommendationResult | RestaurantRecommendationResult | None = Field(default=None)
    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = Field(default=None, max_length=500)
