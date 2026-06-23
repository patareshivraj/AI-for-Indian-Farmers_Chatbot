import time
from typing import List
from app.security_audit.attack_models import AttackPayload, AttackResult, AttackCategory
from app.security_audit.validators import ResponseValidator
from app.execution.orchestrator import Farm360Orchestrator

class AttackRunner:
    """Executes attack payloads against the Orchestrator."""
    
    def __init__(self, orchestrator: Farm360Orchestrator):
        self.orchestrator = orchestrator

    def run_attack(self, payload: AttackPayload) -> AttackResult:
        start_time = time.time()
        success = False
        details = ""
        
        try:
            # Execute through the actual system entrypoint
            # We bypass the API layer and hit the orchestrator directly for unit testing
            result = self.orchestrator.run(user_id=payload.target_user_id, question=payload.query)
            
            # Validate based on category
            if payload.category == AttackCategory.PROMPT_INJECTION:
                success = ResponseValidator.validate_prompt_injection(result)
            elif payload.category == AttackCategory.CROSS_TENANT:
                success = ResponseValidator.validate_tenant_isolation(result)
            elif payload.category == AttackCategory.PII_EXPOSURE:
                # If result is somehow successful, ensure no PII is in string output
                success = ResponseValidator.validate_pii_leak(str(getattr(result, "data", result.error)))
            else:
                # Default validation: should fail if expected_failure is True
                success = (not result.success) if payload.expected_failure else result.success
                
            details = f"Execution Result Success: {result.success}, Intent: {getattr(result.intent, 'value', 'None')}"
                
        except Exception as e:
            # If the system threw an exception (like SecurityError), it defended successfully
            success = payload.expected_failure
            details = str(e)
            
        latency = (time.time() - start_time) * 1000
        
        return AttackResult(
            attack_id=payload.attack_id,
            category=payload.category,
            success=success,
            details=details,
            latency_ms=latency
        )
