from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class AttackCategory(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    CROSS_TENANT = "CROSS_TENANT"
    ROLE_ESCALATION = "ROLE_ESCALATION"
    PII_EXPOSURE = "PII_EXPOSURE"
    MEMORY_POISONING = "MEMORY_POISONING"
    TOOL_INJECTION = "TOOL_INJECTION"
    REASONING_ABUSE = "REASONING_ABUSE"
    LLM_GROUNDING = "LLM_GROUNDING"

class AttackPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attack_id: str
    category: AttackCategory
    query: str
    target_user_id: int
    expected_failure: bool = True

class AttackResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attack_id: str
    category: AttackCategory
    success: bool # True if the system defended successfully
    details: str
    latency_ms: float

class SecurityAuditReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt_injection_score: float = 0.0
    tenant_isolation_score: float = 0.0
    pii_protection_score: float = 0.0
    memory_security_score: float = 0.0
    tool_security_score: float = 0.0
    reasoning_security_score: float = 0.0
    llm_grounding_score: float = 0.0
    overall_score: float = 0.0
    total_attacks: int = 0
    failed_defenses: int = 0
    passed: bool = False
