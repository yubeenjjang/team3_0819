import streamlit as st
import streamlit.components.v1 as components
from typing import cast

from core.travel_kakao_map import (
    build_travel_kakao_map_url,
    extract_travel_places,
)
from core.travel_tool_types import TravelPlanResponse

mock_response: TravelPlanResponse = {
    "provider": "mock",
    "model": "deterministic-travel-tool-mock",
    "request": {
        "city": "부산",
        "check_in": "2026-08-25",
        "check_out": "2026-08-27",
        "guests": 2,
    },
    "tool_calls": [
        {
            "id": "call_attraction_001",
            "name": "recommend_attractions",
            "arguments": {
                "city": "부산",
                "check_in": "2026-08-25",
                "check_out": "2026-08-27",
                "guests": 2,
            },
        },
        {
            "id": "call_restaurant_001",
            "name": "recommend_restaurants",
            "arguments": {
                "city": "부산",
                "check_in": "2026-08-25",
                "check_out": "2026-08-27",
                "guests": 2,
            },
        },
    ],
    "tool_results": [
        {
            "tool_call_id": "call_attraction_001",
            "name": "recommend_attractions",
            "success": True,
            "data": {
                "attractions": [
                    {
                        "name": "해운대해수욕장",
                        "description": "해변 산책과 바다 풍경을 즐길 수 있습니다.",
                        "latitude": 35.1587,
                        "longitude": 129.1604,
                    }
                ]
            },
        },
        {
            "tool_call_id": "call_restaurant_001",
            "name": "recommend_restaurants",
            "success": True,
            "data": {
                "restaurants": [
                    {
                        "name": "해운대 돼지국밥",
                        "description": "부산식 돼지국밥을 즐길 수 있습니다.",
                        "latitude": 35.1631,
                        "longitude": 129.1635,
                        "estimated_price_krw": 10000,
                    }
                ]
            },
        },
    ],
    "answer": "부산 2명 여행에 맞는 관광지와 맛집을 추천했습니다.",
    "latency_ms": 0,
}


st.title("🧭 여행 계획 Tool Use")
st.caption("관광지·맛집 추천 Tool 실행 결과를 지도에서 확인합니다.")

result = cast(
    TravelPlanResponse,
    st.session_state.get("travel_tool_result", mock_response),
)
request = result["request"]

request_columns = st.columns(4)
request_columns[0].metric("여행 지역", request["city"])
request_columns[1].metric("여행 일정", f'{request["check_in"]} ~ {request["check_out"]}')
request_columns[2].metric("여행 인원", f'{request["guests"]}명')
request_columns[3].metric("실행 Tool", f'{len(result["tool_calls"])}개')

st.subheader("여행 계획")
st.write(result["answer"])
st.caption(
    f'{result["provider"]} · {result["model"]} · {result["latency_ms"]} ms'
)

attractions, restaurants = extract_travel_places(result)

st.subheader("카카오맵")
if attractions or restaurants:
    components.iframe(
        build_travel_kakao_map_url(result),
        height=460,
        scrolling=False,
    )
    st.caption("파란 마커는 관광지, 주황 마커는 맛집입니다.")
else:
    st.info("지도에 표시할 추천 장소가 없습니다.")

st.subheader("추천 관광지")
if attractions:
    for attraction in attractions:
        with st.container(border=True):
            st.markdown(f'**{attraction["name"]}**')
            st.write(attraction["description"])
            st.caption(
                f'위도 {attraction["latitude"]:.4f} · '
                f'경도 {attraction["longitude"]:.4f}'
            )
else:
    st.info("추천 관광지가 없습니다.")

st.subheader("추천 맛집")
if restaurants:
    for restaurant in restaurants:
        with st.container(border=True):
            st.markdown(f'**{restaurant["name"]}**')
            st.write(restaurant["description"])
            st.caption(
                f'예상 가격 {restaurant["estimated_price_krw"]:,}원 · '
                f'위도 {restaurant["latitude"]:.4f} · '
                f'경도 {restaurant["longitude"]:.4f}'
            )
else:
    st.info("추천 맛집이 없습니다.")

st.caption("위치, 가격, 영업시간은 실제 방문 전에 다시 확인하세요.")

st.subheader("실행 Trace")
for tool_call in result["tool_calls"]:
    matching_result = next(
        (
            tool_result
            for tool_result in result["tool_results"]
            if tool_result["tool_call_id"] == tool_call["id"]
        ),
        None,
    )
    status = "성공" if matching_result and matching_result["success"] else "실패"
    with st.expander(f'{tool_call["name"]} · {status}', expanded=False):
        st.caption(f'Call ID: {tool_call["id"]}')
        st.markdown("**Tool arguments**")
        st.json(tool_call["arguments"])
        st.markdown("**Tool result**")
        st.json(matching_result or {"success": False, "data": {}})

with st.expander("전체 API 응답 JSON", expanded=False):
    st.json(result)
