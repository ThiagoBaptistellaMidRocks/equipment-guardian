from pydantic import BaseModel
from fastapi import APIRouter

from app.intelligence.equipment_guardian_agent import equipment_guardian_agent

router = APIRouter(prefix="/copilot", tags=["copilot"])


class CopilotChatRequest(BaseModel):
    message: str


class CopilotChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=CopilotChatResponse)
def copilot_chat(payload: CopilotChatRequest) -> CopilotChatResponse:
    return CopilotChatResponse(response=equipment_guardian_agent.chat(payload.message))
