from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any

from app.execution.orchestrator import Farm360Orchestrator
from app.context.builder import ContextBuilder
from app.router.router import QueryRouter
from app.execution.planner import ExecutionPlanner
from app.execution.executor import ExecutionEngine
from app.execution.resolver import AgentResolver

from app.repositories.user_repo import UserRepository
from app.repositories.farmer_repo import FarmerRepository
from app.repositories.consultant_repo import ConsultantRepository

from app.llm.llm_service import LLMService
from app.response.models import ResponsePayload, ResponseType
from app.context.models import LanguageEnum

from app.access.guard import ToolExecutionGuard
from app.repositories.base import SessionLocal
from app.tools.registry import ExecutableToolRegistry
from app.execution.agents.database_agent import DatabaseAgent
from app.execution.agents.knowledge_agent import KnowledgeAgent
from app.execution.agents.scheme_agent import SchemeAgent

app = FastAPI(
    title="Farm360 AI Copilot API",
    description="Secure deterministic agricultural intelligence API",
    version="1.0.0"
)

# Dependency Injection
def get_orchestrator():
    context_builder = ContextBuilder(UserRepository(), FarmerRepository(), ConsultantRepository())
    router = QueryRouter()
    planner = ExecutionPlanner()
    
    db_session = SessionLocal()
    guard = ToolExecutionGuard()
    tool_registry = ExecutableToolRegistry(guard, db_session)
    
    agents = [
        DatabaseAgent(tool_registry),
        KnowledgeAgent(tool_registry),
        SchemeAgent(tool_registry)
    ]
    
    agent_resolver = AgentResolver(agents)
    engine_exec = ExecutionEngine(agent_resolver)
    
    return Farm360Orchestrator(context_builder, router, planner, engine_exec)

def get_llm_service():
    return LLMService(model_name="llama-3.3-70b-versatile")

class ChatRequest(BaseModel):
    user_id: int
    query: str

class ChatResponse(BaseModel):
    success: bool
    intent: str | None
    data: list | dict | None
    response: str
    execution_time_ms: int

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest, 
    orchestrator: Farm360Orchestrator = Depends(get_orchestrator),
    llm: LLMService = Depends(get_llm_service)
):
    try:
        # 1. Run Deterministic Pipeline
        exec_result = orchestrator.run(user_id=request.user_id, question=request.query)
        
        if not exec_result.success:
            return ChatResponse(
                success=False,
                intent=exec_result.intent.value if exec_result.intent else None,
                data=None,
                response=exec_result.error or "Failed to execute query.",
                execution_time_ms=exec_result.execution_time_ms
            )

        # 2. Build LLM Payload
        
        # Map intent to response type
        intent_to_type = {
            "CROP_QUERY": ResponseType.CROP_RESPONSE,
            "MARKET_QUERY": ResponseType.MARKET_RESPONSE,
        }
        resp_type = intent_to_type.get(exec_result.intent.value if exec_result.intent else "", ResponseType.UNKNOWN_RESPONSE)

        payload = ResponsePayload(
            success=True,
            response_type=resp_type,
            title="Copilot Response",
            content=exec_result.data if exec_result.data else {},
            source="DATABASE",
            language=LanguageEnum.ENGLISH # Should ideally come from user context
        )

        # 3. Format via LLM
        llm_response = llm.process(payload)

        return ChatResponse(
            success=True,
            intent=exec_result.intent.value if exec_result.intent else None,
            data=exec_result.data,
            response=llm_response.content,
            execution_time_ms=exec_result.execution_time_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
