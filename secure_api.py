from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# --- App & Middleware ---
app = FastAPI(title="Secure FastAPI Example")

# Force HTTPS (only in production!)
# app.add_middleware(HTTPSRedirectMiddleware)

# Add secure headers manually
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

app.add_middleware(SecureHeadersMiddleware)

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-client-app.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate Limiting ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded. Try again later."},
    )

# --- Authorization ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_tokens_db = {
    "token123": {"username": "alice", "scopes": ["read"]},
    "token456": {"username": "bob", "scopes": ["write"]}
}

def get_current_user(token: str = Depends(oauth2_scheme)):
    if token not in fake_tokens_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return fake_tokens_db[token]

# --- Routes ---

@app.get("/public")
@limiter.limit("5/minute")
def public(request: Request):
    return {"message": "This is a public endpoint."}

@app.get("/private")
@limiter.limit("3/minute")
def private(request: Request, user=Depends(get_current_user)):
    return {"message": f"Hello {user['username']}, you are authorized."}

