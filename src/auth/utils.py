import re
from .constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH

def validate_password(password: str) -> bool:
    """
    Validate password meets minimum requirements:
    - Length between MIN_PASSWORD_LENGTH and MAX_PASSWORD_LENGTH
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        return False
    
    if not re.search(r"[A-Z]", password):  # Uppercase
        return False
    
    if not re.search(r"[a-z]", password):  # Lowercase
        return False
    
    if not re.search(r"\d", password):  # Digit
        return False
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Special char
        return False
    
    return True 