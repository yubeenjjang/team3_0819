from fastapi import FastAPI

from app.routers.agent_router import agent_router


OPENAPI_TAGS = [
    {
        "name": "01 · LLM",
        "description": "LLM 기본, Provider 비교, 프롬프트, 멀티모달 API",
    },
    {
        "name": "02 · Structured Output",
        "description": "Pydantic 검증과 구조화 출력 API",
    },
    {
        "name": "03 · Tool Use",
        "description": "Tool 스키마, 선택, 안전 실행, Agent Loop API",
    },
]


app = FastAPI(
    title="Mini Agent 03 · Tool Use",
    description="01 LLM → 02 Structured Output → 03 Tool Use 단계별 누적 API",
    openapi_tags=OPENAPI_TAGS,
)
app.include_router(agent_router)
