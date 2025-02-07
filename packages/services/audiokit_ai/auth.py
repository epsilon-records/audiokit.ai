from fastapi import Header, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
import jwt

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key"  # In production, load this from an environment variable

def verify_jwt(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Return decoded token payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_api_key(api_key: str = Header(None)):
    if api_key != "expected-api-key":
        raise HTTPException(status_code=403, detail="Invalid API key") 