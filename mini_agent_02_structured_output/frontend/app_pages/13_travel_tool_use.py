from datetime import date, timedelta
from typing import Any

import streamlit as st

from clients.travel_tool_client import create_travel_plan
from core.api_client import BackendAPIError


CITIES = ["서울", "부산", "제주", "강릉", "인천", "대전", "대구", "광주", "전주", "경주"]
PROVIDERS = ["mock", "gemini", "openai", "ollama"]
RESULT_STATE_KEY = "travel_tool_use_result"
REQUEST_STATE_KEY = "travel_tool_use_request"


def validate_inputs(check_in: date, check_out: date, guests: int) -> list[str]:
    errors: list[str] = []
    if check_in <= date.today():
        errors.append("여행 시작일은 오늘 이후여야 합니다.")
    if check_out <= check_in:
        errors.append("여행 종료일은 시작일 이후여야 합니다.")
    if not 1 <= guests <= 10:
        errors.append("여행 인원은 1명부터 10명까지 선택할 수 있습니다.")
    return errors


def user_error_message(error: BackendAPIError) -> str:
    message = str(error)
    if "(422)" in message:
        return f"입력값을 확인해 주세요. {message}"
    if "(502)" in message:
        return f"Provider 호출에 실패했습니다. 잠시 후 다시 시도해 주세요. {message}"
    if "(503)" in message:
        return f"여행 정보 조회에 실패했습니다. 잠시 후 다시 시도해 주세요. {message}"
    return message


st.title("🧭 여행 계획 Tool Use")
st.caption("지역, 일정, 인원을 선택하면 검증된 여행 조회 Tool로 계획을 생성합니다.")

today = date.today()
default_check_in = today + timedelta(days=1)
default_check_out = default_check_in + timedelta(days=2)

provider = st.selectbox("Provider", PROVIDERS, index=0)
city = st.selectbox("여행 지역", CITIES, index=0)

date_column, guest_column = st.columns(2)
with date_column:
    check_in = st.date_input(
        "여행 시작일",
        value=default_check_in,
        min_value=default_check_in,
    )
    check_out = st.date_input(
        "여행 종료일",
        value=default_check_out,
        min_value=default_check_in,
    )
with guest_column:
    guests = int(
        st.number_input(
            "여행 인원",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
        )
    )

if provider in {"gemini", "openai"}:
    st.info("선택한 Provider는 Cloud API 호출 비용이 발생할 수 있습니다.")

validation_errors = validate_inputs(check_in, check_out, guests)
for validation_error in validation_errors:
    st.warning(validation_error)

if st.button(
    "계획 생성",
    type="primary",
    disabled=bool(validation_errors),
    use_container_width=True,
):
    try:
        with st.spinner("여행 계획을 생성하는 중입니다..."):
            result: dict[str, Any] = create_travel_plan(
                provider=provider,
                city=city,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
            )
        st.session_state[RESULT_STATE_KEY] = result
        st.session_state[REQUEST_STATE_KEY] = {
            "provider": provider,
            "city": city,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests,
        }
        st.success("여행 계획 응답을 받았습니다.")
    except BackendAPIError as error:
        st.session_state.pop(RESULT_STATE_KEY, None)
        st.session_state.pop(REQUEST_STATE_KEY, None)
        st.error(user_error_message(error))

# Frontend B integration boundary:
# Read st.session_state[RESULT_STATE_KEY] below this line and render only the
# map, recommendation cards, Tool Call/Result, and execution Trace here.
