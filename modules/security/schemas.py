# Security schemes
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
