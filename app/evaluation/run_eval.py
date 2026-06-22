import os
import sys

# Ensure project root is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.context.builder import ContextBuilder
from app.router.router import QueryRouter
from app.execution.planner import ExecutionPlanner
from app.execution.executor import ExecutionEngine
from app.execution.resolver import AgentResolver
from app.execution.agents.database_agent import DatabaseAgent
from app.execution.agents.knowledge_agent import KnowledgeAgent
from app.execution.agents.scheme_agent import SchemeAgent
from app.execution.orchestrator import Farm360Orchestrator
from app.tools.registry import ExecutableToolRegistry
from app.response.response_engine import ResponseEngine
from app.llm.llm_service import LLMService
from app.evaluation.evaluator import EvaluatorHarness

def run():
    print("Initializing Farm360 AI Evaluation Harness...")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.access.guard import ToolExecutionGuard
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    guard = ToolExecutionGuard()
    
    registry = ExecutableToolRegistry(guard=guard, db_session=db_session)
    agents = [
        DatabaseAgent(registry),
        KnowledgeAgent(registry),
        SchemeAgent(registry)
    ]
    
    from app.repositories.user_repo import UserRepository
    from app.repositories.farmer_repo import FarmerRepository
    from app.repositories.consultant_repo import ConsultantRepository
    
    orchestrator = Farm360Orchestrator(
        context_builder=ContextBuilder(
            user_repo=UserRepository(db_session),
            farmer_repo=FarmerRepository(db_session),
            consultant_repo=ConsultantRepository(db_session)
        ),
        query_router=QueryRouter(),
        execution_planner=ExecutionPlanner(),
        execution_engine=ExecutionEngine(AgentResolver(agents))
    )
    
    response_engine = ResponseEngine()
    llm_service = LLMService(model_name="gemini-2.5-flash-eval")
    
    harness = EvaluatorHarness(
        orchestrator=orchestrator,
        response_engine=response_engine,
        llm_service=llm_service
    )
    
    print("Running evaluations across dataset...")
    # Make reports dir
    os.makedirs("app/evaluation/reports", exist_ok=True)
    
    scorecard = harness.run_evaluation()
    harness.export_report()
    
    print("\n================ FINAL SCORECARD ================")
    print(f"Total Queries Tested : {scorecard.total_queries}")
    print(f"Intent Accuracy      : {scorecard.intent_accuracy}%")
    print(f"Tool Accuracy        : {scorecard.tool_accuracy}%")
    print(f"Permission Violations: {scorecard.permission_violations}")
    print(f"PII Leaks            : {scorecard.pii_leaks}")
    print(f"Hallucination Rate   : {scorecard.hallucination_rate}%")
    print(f"Latency p95          : {scorecard.latency_p95} ms")
    print(f"System Readiness     : {scorecard.readiness}")
    print("=================================================")
    
    if scorecard.readiness == "PASS":
        print("✅ Farm360 AI Copilot is APPROVED for Pilot Deployment.")
    else:
        print("❌ System FAILED evaluation thresholds.")
        sys.exit(1)

if __name__ == "__main__":
    run()
