from app.response.models import SupportedLanguage
from app.context.models import UserContext

class LanguageResolver:
    """Resolves language from user context or default."""
    
    def resolve(self, context: UserContext = None) -> SupportedLanguage:
        # Currently defaults to EN. In production, this would look at context.user.language
        # For our tests, we will allow injecting or defaulting.
        if context and hasattr(context.user, 'language') and context.user.language:
            lang_str = str(context.user.language).lower()
            if lang_str in ['hi', 'hindi']:
                return SupportedLanguage.HI
            elif lang_str in ['mr', 'marathi']:
                return SupportedLanguage.MR
        return SupportedLanguage.EN
