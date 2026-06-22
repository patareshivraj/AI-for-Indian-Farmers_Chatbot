from app.execution.models import ExecutionResult
from app.context.models import UserContext
from app.response.models import ResponsePayload, SupportedLanguage
from app.response.formatter import ResponseFormatter
from app.response.language import LanguageResolver

class ResponseEngine:
    """The central orchestrator for deterministic response generation."""
    
    def __init__(self):
        self.formatter = ResponseFormatter()
        self.language_resolver = LanguageResolver()

    def generate(self, result: ExecutionResult, context: UserContext = None, force_lang: SupportedLanguage = None) -> ResponsePayload:
        """
        Transforms a raw ExecutionResult into a structured ResponsePayload.
        """
        # Resolve language
        lang = force_lang if force_lang else self.language_resolver.resolve(context)
        
        # Route to correct formatter
        if result.success:
            return self.formatter.format_success(result, lang)
        else:
            return self.formatter.format_error(result, lang)
