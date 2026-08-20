from typing import Any

from core.kakao_map import build_kakao_map_url


def extract_places(tool_results: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract map-ready attractions and restaurants from normalized Tool results."""
    attractions: list[dict[str, Any]] = []
    restaurants: list[dict[str, Any]] = []
    for result in tool_results:
        data = result.get("data") or {}
        if result.get("name") == "recommend_attractions":
            attractions.extend(data.get("attractions", []))
        if result.get("name") == "recommend_restaurants":
            restaurants.extend(data.get("restaurants", []))
    return attractions, restaurants


def build_travel_map_url(tool_results: list[dict[str, Any]]) -> str | None:
    attractions, restaurants = extract_places(tool_results)
    if not attractions and not restaurants:
        return None
    return build_kakao_map_url(attractions, restaurants)
