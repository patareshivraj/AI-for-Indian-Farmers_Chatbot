import time
from typing import List
from app.llm.models import LLMRequest, LLMResponse, LLMTrace
from app.response.models import ResponsePayload
from app.llm.validator import PayloadValidator, OutputValidator
from app.llm.guardrails import GroundingGuard
from app.llm.fallback import FallbackFormatter
from app.llm.generator import ResponseGenerator
from datetime import datetime

class LLMService:
    """Orchestrates LLM generation with strict fallback and validation."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.payload_validator = PayloadValidator()
        self.guard = GroundingGuard()
        self.generator = ResponseGenerator(model_name)
        self.output_validator = OutputValidator()
        self.fallback = FallbackFormatter()
        self.traces: List[LLMTrace] = []

    def process(self, payload: ResponsePayload) -> LLMResponse:
        start_time = time.time()
        
        # 1. Validate Structure
        if not self.payload_validator.validate(payload):
            return self._handle_fallback(payload, start_time, "Invalid Payload Structure")
            
        # 2. Run Guardrails
        if not self.guard.check(payload):
            return self._handle_fallback(payload, start_time, "Guardrail Violation")
            
        # 3. Create Request
        request = LLMRequest(
            response_payload=payload,
            language=payload.language
        )
        
        # 4. Generate Content
        try:
            llm_response = self.generator.generate(request)
            
            # 5. Validate Output Grounding
            if not self.output_validator.validate(payload, llm_response.content):
                raise ValueError("Output validation failed (Hallucination detected)")
                
            self._record_trace(latency_ms=int((time.time() - start_time) * 1000), tokens=llm_response.tokens_used, success=True, fallback=False)
            return llm_response
            
        except Exception as e:
            # Catch Gemini/OpenAI network errors, rate limits, or validation failures
            return self._handle_fallback(payload, start_time, str(e))
            
    def _handle_fallback(self, payload: ResponsePayload, start_time: float, reason: str) -> LLMResponse:
        fallback_content = self.fallback.format(payload)
        latency = int((time.time() - start_time) * 1000)
        
        self._record_trace(latency_ms=latency, tokens=0, success=False, fallback=True)
        
        return LLMResponse(
            success=payload.success,
            content=fallback_content,
            source=payload.source,
            model="fallback",
            tokens_used=0,
            generated_at=datetime.utcnow(),
            fallback_used=True
        )
        
    def _record_trace(self, latency_ms: int, tokens: int, success: bool, fallback: bool):
        trace = LLMTrace(
            model_name=self.model_name if not fallback else "fallback",
            latency_ms=latency_ms,
            tokens_used=tokens,
            success=success,
            fallback_used=fallback
        )
        self.traces.append(trace)
