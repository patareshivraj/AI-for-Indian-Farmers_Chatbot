from app.response.models import ResponseType, SupportedLanguage

class ResponseTemplates:
    """Deterministic phrase dictionaries for titles and generic messages."""
    
    _titles = {
        ResponseType.PROFILE_RESPONSE: {
            SupportedLanguage.EN: "Your Profile Details",
            SupportedLanguage.HI: "आपकी प्रोफ़ाइल विवरण",
            SupportedLanguage.MR: "तुमचे प्रोफाइल तपशील"
        },
        ResponseType.LAND_RESPONSE: {
            SupportedLanguage.EN: "Land Records",
            SupportedLanguage.HI: "भूमि रिकॉर्ड",
            SupportedLanguage.MR: "जमीन रेकॉर्ड"
        },
        ResponseType.CROP_RESPONSE: {
            SupportedLanguage.EN: "Active Crops",
            SupportedLanguage.HI: "सक्रिय फसलें",
            SupportedLanguage.MR: "सक्रिय पिके"
        },
        ResponseType.INVENTORY_RESPONSE: {
            SupportedLanguage.EN: "Farm Inventory",
            SupportedLanguage.HI: "फार्म इन्वेंटरी",
            SupportedLanguage.MR: "फार्म इन्व्हेंटरी"
        },
        ResponseType.WEATHER_RESPONSE: {
            SupportedLanguage.EN: "Weather Update",
            SupportedLanguage.HI: "मौसम अपडेट",
            SupportedLanguage.MR: "हवामान अपडेट"
        },
        ResponseType.MARKET_RESPONSE: {
            SupportedLanguage.EN: "Market Prices",
            SupportedLanguage.HI: "बाजार मूल्य",
            SupportedLanguage.MR: "बाजार भाव"
        },
        ResponseType.SCHEME_RESPONSE: {
            SupportedLanguage.EN: "Government Schemes",
            SupportedLanguage.HI: "सरकारी योजनाएं",
            SupportedLanguage.MR: "सरकारी योजना"
        },
        ResponseType.KNOWLEDGE_RESPONSE: {
            SupportedLanguage.EN: "Farming Information",
            SupportedLanguage.HI: "खेती की जानकारी",
            SupportedLanguage.MR: "शेती विषयक माहिती"
        },
        ResponseType.ERROR_RESPONSE: {
            SupportedLanguage.EN: "Error Occurred",
            SupportedLanguage.HI: "त्रुटि हुई",
            SupportedLanguage.MR: "त्रुटी आली"
        },
        ResponseType.UNKNOWN_RESPONSE: {
            SupportedLanguage.EN: "Unknown Request",
            SupportedLanguage.HI: "अज्ञात अनुरोध",
            SupportedLanguage.MR: "अज्ञात विनंती"
        }
    }

    def get_title(self, response_type: ResponseType, lang: SupportedLanguage) -> str:
        return self._titles.get(response_type, {}).get(lang, "Information")
