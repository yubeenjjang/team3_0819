"""Backend B의 카카오맵 여행 추천 API 계약 테스트입니다.

Backend A의 Schema·Provider 모듈이 병합되기 전에는 이 파일 전체를 건너뜁니다.
A 병합 후에는 전용 Router를 독립 FastAPI 앱에 등록해 B 계층을 검증합니다.
"""

from types import SimpleNamespace

import pytest


pytest.importorskip(
    "app.map_travel.schemas",
    reason="Backend A의 map_travel Schema가 병합된 뒤 실행합니다.",
)
pytest.importorskip(
    "app.map_travel.provider_service",
    reason="Backend A의 Provider Service가 병합된 뒤 실행합니다.",
)

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.map_travel.provider_service import (
    MapTravelOutputValidationError,
    MapTravelProviderError,
)
from app.routers.map_travel_router import map_travel_router


app = FastAPI()
app.include_router(map_travel_router)
client = TestClient(app)


VALID_CONTENT = {
    "destination": "부산",
    "nights": 2,
    "days": 3,
    "summary": "부산의 대표 장소를 둘러보는 2박 3일 여행입니다.",
    "landmarks": [
        {
            "name": "해운대해수욕장",
            "description": "해변 산책을 즐길 수 있는 장소입니다.",
            "latitude": 35.1587,
            "longitude": 129.1604,
            "category": "beach",
        }
    ],
    "foods": [
        {
            "name": "돼지국밥",
            "estimated_price_krw": 10000,
            "description": "부산을 대표하는 국밥입니다.",
            "latitude": 35.1631,
            "longitude": 129.1635,
        }
    ],
    "cautions": ["가격과 영업시간은 방문 전에 확인하세요."],
}


def provider_result() -> SimpleNamespace:
    return SimpleNamespace(
        provider="mock",
        model="deterministic-map-travel-mock",
        content=VALID_CONTENT,
        latency_ms=0,
    )


def test_map_travel_returns_valid_mock_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.map_travel.service.generate_map_travel",
        lambda provider, message: provider_result(),
    )

    response = client.post(
        "/api/structured/map-travel",
        json={"provider": "mock", "message": "부산 2박 3일 여행을 추천해 주세요."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "mock",
        "model": "deterministic-map-travel-mock",
        "content": VALID_CONTENT,
        "latency_ms": 0,
    }


def test_map_travel_uses_default_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected: dict[str, str] = {}

    def fake_generate(provider: str, message: str) -> SimpleNamespace:
        selected["provider"] = provider
        return provider_result()

    monkeypatch.setattr("app.map_travel.service.generate_map_travel", fake_generate)

    response = client.post(
        "/api/structured/map-travel",
        json={"message": "부산 당일치기 여행을 추천해 주세요."},
    )

    assert response.status_code == 200
    assert selected["provider"] == "mock"


@pytest.mark.parametrize(
    "payload",
    [
        {"provider": "mock", "message": ""},
        {"provider": "mock", "message": "   "},
        {"provider": "mock", "message": "가" * 4001},
        {"provider": "invalid", "message": "부산 여행"},
    ],
)
def test_map_travel_rejects_invalid_request(payload: dict[str, str]) -> None:
    response = client.post("/api/structured/map-travel", json=payload)

    assert response.status_code == 422


def test_map_travel_maps_output_validation_error_to_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_validation(provider: str, message: str) -> None:
        raise MapTravelOutputValidationError("internal schema detail")

    monkeypatch.setattr("app.map_travel.service.generate_map_travel", fail_validation)

    response = client.post(
        "/api/structured/map-travel",
        json={"provider": "mock", "message": "부산 여행"},
    )

    assert response.status_code == 422
    assert "internal schema detail" not in response.text


def test_map_travel_maps_provider_error_to_502(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_provider(provider: str, message: str) -> None:
        raise MapTravelProviderError("secret provider detail")

    monkeypatch.setattr("app.map_travel.service.generate_map_travel", fail_provider)

    response = client.post(
        "/api/structured/map-travel",
        json={"provider": "openai", "message": "부산 여행"},
    )

    assert response.status_code == 502
    assert "secret provider detail" not in response.text


def test_openapi_exposes_map_travel_contract() -> None:
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/structured/map-travel"]["post"]

    assert operation["tags"] == ["02 · Prompt & Structured Output"]
    assert "MapTravelRequest" in schema["components"]["schemas"]
    assert "MapTravelResponse" in schema["components"]["schemas"]
