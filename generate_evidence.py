import sys
import os
import json
import time
from sqlalchemy import text
from app.repositories.base import engine
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

def generate_evidence():
    evidence = []
    
    # 1. Real DB Query Result
    evidence.append("=== 1. REAL DATABASE QUERY RESULT ===\n")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, crop_name, is_crop_planted FROM farmer_crop_details WHERE farmer_id = '4' LIMIT 2")).mappings().fetchall()
            evidence.append(f"[SQL]: SELECT id, crop_name, is_crop_planted FROM farmer_crop_details WHERE farmer_id = '4' LIMIT 2")
            evidence.append(f"[Raw Output]: {json.dumps([dict(r) for r in result], indent=2)}\n")
    except Exception as e:
        evidence.append(f"[Error]: {str(e)}\n")

    # 2. Chatbot Answer & 3. Groq Model Response
    evidence.append("=== 2 & 3. CHATBOT ANSWER & GROQ MODEL RESPONSE ===\n")
    try:
        # Get raw data
        farmer_repo = FarmerRepository()
        raw_data = farmer_repo.get_farm_metrics(user_id=4)
        evidence.append(f"[User Query]: What active crops do I have?")
        evidence.append(f"[Execution Engine Output (Pre-LLM)]: {raw_data}\n")
        
        # Pass to Groq LLM
        llm = LLMService(model_name="llama-3.3-70b-versatile")
        payload = ResponsePayload(
            success=True,
            response_type=ResponseType.CROP_RESPONSE,
            title="Active Crops",
            content=raw_data,
            source="DATABASE",
            language=LanguageEnum.ENGLISH
        )
        
        start_time = time.time()
        llm_response = llm.process(payload)
        latency = int((time.time() - start_time) * 1000)
        
        evidence.append(f"[Groq API Call Trace]")
        evidence.append(f" - Model: {llm_response.model}")
        evidence.append(f" - Latency: {latency} ms")
        evidence.append(f" - Tokens Used: {llm_response.tokens_used}")
        evidence.append(f" - Fallback Used: {llm_response.fallback_used}\n")
        
        evidence.append(f"[Final Chatbot Answer (from Groq)]:\n{llm_response.content}\n")
        
    except Exception as e:
        evidence.append(f"[Error]: {str(e)}\n")

        # 4. Denied Cross-Tenant Request
    evidence.append("=== 4. DENIED UNAUTHORIZED REQUEST ===\n")
    try:
        from app.access.guard import ToolExecutionGuard
        from app.access.models import ToolName
        from app.context.builder import ContextBuilder
        
        context_builder = ContextBuilder(UserRepository(), FarmerRepository(), ConsultantRepository())
        context = context_builder.build_context(user_id=4)
        evidence.append(f"[Context Built]: User {context.user.user_id}, Role: {context.user.role.value}")
        
        guard = ToolExecutionGuard()
        evidence.append(f"[Attempted Action]: {ToolName.GET_MY_PROFILE.value} on Target Farmer ID 99")
        
        try:
            guard.validate(context, tool_name=ToolName.GET_MY_PROFILE, target_farmer_id=99)
            evidence.append(f"[Execution Success]: True")
        except Exception as guard_error:
            evidence.append(f"[Execution Success]: False")
            evidence.append(f"[Security/Permission Error]: {str(guard_error)}\n")
            
    except Exception as e:
        evidence.append(f"[Error]: {str(e)}\n")

    # Write out
    with open("evidence_package.md", "w") as f:
        f.write("# Farm360 AI Copilot: Final Evidence Package\n\n")
        f.write("\n".join(evidence))
        
    print("evidence_package.md generated successfully.")

if __name__ == "__main__":
    generate_evidence()
