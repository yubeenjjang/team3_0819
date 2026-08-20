from datetime import date, timedelta
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from clients.travel_tool_client import generate_travel_plan
from core.api_client import BackendAPIError
from core.travel_kakao_map import build_travel_map_url, extract_places


CITIES = ["서울", "부산", "제주", "강릉", "인천", "대전", "대구", "광주", "전주", "경주"]


st.title("🧭 여행 계획 Tool Use")
st.caption("지역, 여행 일정, 인원을 선택하면 안전한 Tool Use 흐름으로 관광지와 맛집을 추천합니다.")

left, right = st.columns(2)
with left:
    provider = st.selectbox("Provider", ["mock", "openai", "gemini", "ollama"], index=0)
    city = st.selectbox("여행 지역", CITIES, index=1)
    guests = st.number_input("여행 인원", min_value=1, max_value=10, value=2, step=1)
with right:
    check_in = st.date_input("여행 일정 시작일", value=date.today() + timedelta(days=1), min_value=date.today())
    check_out = st.date_input("여행 일정 종료일", value=date.today() + timedelta(days=3), min_value=date.today() + timedelta(days=1))
    if provider != "mock":
        st.info("실제 Provider는 각 API 키 또는 Ollama 서버·모델 설정이 필요합니다.")

date_valid = check_out > check_in
if not date_valid:
    st.error("여행 일정 종료일은 시작일 이후여야 합니다.")

if st.button("여행 계획 생성", type="primary", disabled=not date_valid):
    try:
        with st.spinner("관광지와 맛집을 조회하는 중입니다..."):
            st.session_state.travel_tool_result = generate_travel_plan(
                provider, city, check_in, check_out, int(guests)
            )
    except BackendAPIError as error:
        st.error(str(error))

result: dict[str, Any] | None = st.session_state.get("travel_tool_result")
if result:
    request = result.get("request", {})
    tool_results = result.get("tool_results", [])
    attractions, restaurants = extract_places(tool_results)
    st.subheader(f"{request.get('city', city)} 여행 계획")
    st.caption(
        f"{result.get('provider', '')} · {result.get('model', '')} · "
        f"{result.get('latency_ms', 0)} ms"
    )
    st.write(result.get("answer", ""))

    st.subheader("카카오맵")
    map_url = build_travel_map_url(tool_results)
    if map_url:
        components.iframe(map_url, height=460, scrolling=False)
        st.caption("파란 마커는 관광지, 주황 마커는 맛집입니다.")
    else:
        st.warning("지도에 표시할 유효한 좌표가 없습니다.")

    first, second = st.columns(2)
    with first:
        st.subheader(f"추천 관광지 ({len(attractions)}곳)")
        for attraction in attractions:
            with st.container(border=True):
                st.markdown(f"**{attraction.get('name', '이름 없음')}** · {attraction.get('category', '관광지')}")
                st.write(attraction.get("description", "설명이 없습니다."))
    with second:
        st.subheader(f"추천 맛집 ({len(restaurants)}곳)")
        for restaurant in restaurants:
            with st.container(border=True):
                st.markdown(f"**{restaurant.get('name', '이름 없음')}** · {int(restaurant.get('estimated_price_krw', 0)):,}원")
                st.write(restaurant.get("description", "설명이 없습니다."))

    with st.expander("Tool Call · Tool Result · 실행 Trace"):
        st.markdown("**Tool Call**")
        st.json(result.get("tool_calls", []))
        st.markdown("**Tool Result**")
        st.json(tool_results)
        st.markdown("**최종 응답**")
        st.json(result)
