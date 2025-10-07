"""
JWT authentication for Sentio
"""
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Add encode/decode helpers here
