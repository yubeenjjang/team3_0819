from fastapi import FastAPI

from app.routers.agent_router import agent_router


OPENAPI_TAGS = [
    {"name": "00. 환경 상태", "description": "백엔드와 Provider 설정을 확인합니다."},
    {"name": "01. LLM에서 Agent로", "description": "LLM 호출, 분류, Provider 비교와 멀티모달 기능입니다."},
    {"name": "02. Prompt와 구조화 출력", "description": "프롬프트 구성과 Pydantic 기반 구조화 출력 검증입니다."},
    {"name": "03. Tool Use", "description": "Tool 정의, 선택, 검증·실행 및 Agent Loop입니다."},
]


app = FastAPI(title="Mini Agent 03 · Tool Use", openapi_tags=OPENAPI_TAGS)
app.include_router(agent_router)
