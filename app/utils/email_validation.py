import re
from flask import abort

def validate_email(email: str) -> bool:
    """
    Validates that the email is not empty and that it matches one of the allowed domains.
    Allowed domains: conceptgroup-ng.com, rosabon-finance.com, rosabon-finance.net, concept-nova.com.
    
    Raises:
        400 HTTP error if the email is not provided or does not match the allowed domains.
    
    Returns:
        True if the email is valid.
    """
    if not email:
        abort(400, description="Email is required.")

    # Build the regex pattern with allowed domains
    pattern = (
        r"^[A-Za-z0-9+_.-]+@"
        r"(conceptgroup-ng\.com|rosabon-finance\.com|rosabon-finance\.net|concept-nova\.com)$"
    )
    
    if not re.match(pattern, email):
        abort(400, description="The provided email is not allowed. Please register using your company email address.")
    
    return True
