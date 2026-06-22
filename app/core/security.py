def mask_mobile(mobile_number: str | None) -> str | None:
    """Masks a mobile number, exposing only first two and last three digits."""
    if not mobile_number:
        return None
    mobile_str = str(mobile_number)
    if len(mobile_str) < 5:
        return "****"
    return f"{mobile_str[:2]}{'X' * (len(mobile_str) - 5)}{mobile_str[-3:]}"

def sanitize_user_data(user_data: dict) -> dict:
    """Sanitizes user dictionary, completely dropping restricted fields."""
    restricted_keys = {"password", "email", "adhar_no", "pan_no", "property_uid"}
    sanitized = {k: v for k, v in user_data.items() if k not in restricted_keys}
    
    if "mobile_number" in sanitized:
        sanitized["mobile_number"] = mask_mobile(sanitized["mobile_number"])
        
    return sanitized

def sanitize_land_record(land_record: dict) -> dict:
    """Sanitizes land record, dropping restricted PII."""
    restricted_keys = {"adhar_no", "pan_no", "property_uid"}
    return {k: v for k, v in land_record.items() if k not in restricted_keys}
