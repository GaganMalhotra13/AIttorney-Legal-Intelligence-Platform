# backend/routers/auth.py — complete strengthened version
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from datetime import datetime, timedelta
import bcrypt, os
from jose import jwt, JWTError
from database import users_col, refresh_tokens_col
import secrets

router   = APIRouter(prefix="/api/auth", tags=["auth"])
SECRET   = os.getenv("JWT_SECRET")
ALG      = "HS256"
ACCESS_EXP  = 60 * 60        # 1 hour
REFRESH_EXP = 60 * 60 * 24 * 30  # 30 days
security = HTTPBearer()

# ── Token helpers ─────────────────────────────────────────────
def make_access_token(user_id: str, email: str) -> str:
    return jwt.encode({
        "sub":   user_id,
        "email": email,
        "type":  "access",
        "exp":   datetime.utcnow() + timedelta(seconds=ACCESS_EXP),
    }, SECRET, algorithm=ALG)

def make_refresh_token() -> str:
    return secrets.token_urlsafe(64)

async def get_current_user_dep(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Invalid or missing authorization token")

    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=[ALG])
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token payload")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(401, "User not found")

    return user

async def save_refresh_token(user_id: str, token: str):
    await refresh_tokens_col.insert_one({
        "user_id":    user_id,
        "token":      token,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(seconds=REFRESH_EXP),
        "revoked":    False,
    })

# ── Schemas ───────────────────────────────────────────────────
class RegisterBody(BaseModel):
    email:    EmailStr
    password: str
    name:     str

class LoginBody(BaseModel):
    email:    EmailStr
    password: str

class RefreshBody(BaseModel):
    refresh_token: str

class UpdateProfileBody(BaseModel):
    name:     str | None = None
    phone:    str | None = None
    location: str | None = None

# ── Endpoints ─────────────────────────────────────────────────
@router.post("/register")
async def register(body: RegisterBody):
    if await users_col.find_one({"email": body.email}):
        raise HTTPException(400, "Email already registered")
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    hashed = bcrypt.hashpw(body.password[:72].encode(), bcrypt.gensalt()).decode()
    result = await users_col.insert_one({
        "email":      body.email,
        "name":       body.name,
        "password":   hashed,
        "phone":      None,
        "location":   None,
        "plan":       "free",
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "login_count":1,
    })

    user_id       = str(result.inserted_id)
    access_token  = make_access_token(user_id, body.email)
    refresh_token = make_refresh_token()
    await save_refresh_token(user_id, refresh_token)

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "expires_in":    ACCESS_EXP,
        "user": {
            "id":    user_id,
            "email": body.email,
            "name":  body.name,
            "plan":  "free",
        }
    }


@router.post("/login")
async def login(body: LoginBody):
    user = await users_col.find_one({"email": body.email})
    if not user:
        raise HTTPException(401, "Invalid credentials")
    if not bcrypt.checkpw(body.password[:72].encode(), user["password"].encode()):
        raise HTTPException(401, "Invalid credentials")

    user_id = str(user["_id"])

    # Update last login
    await users_col.update_one(
        {"_id": user["_id"]},
        {"$set":  {"last_login": datetime.utcnow()},
         "$inc":  {"login_count": 1}}
    )

    access_token  = make_access_token(user_id, user["email"])
    refresh_token = make_refresh_token()
    await save_refresh_token(user_id, refresh_token)

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "expires_in":    ACCESS_EXP,
        "user": {
            "id":       user_id,
            "email":    user["email"],
            "name":     user["name"],
            "phone":    user.get("phone"),
            "location": user.get("location"),
            "plan":     user.get("plan", "free"),
        }
    }


@router.post("/refresh")
async def refresh(body: RefreshBody):
    """Exchange a refresh token for a new access token — no re-login needed."""
    record = await refresh_tokens_col.find_one({
        "token":   body.refresh_token,
        "revoked": False,
    })
    if not record:
        raise HTTPException(401, "Invalid or expired refresh token")
    if record["expires_at"] < datetime.utcnow():
        raise HTTPException(401, "Refresh token expired. Please log in again.")

    user = await users_col.find_one({"_id": ObjectId(record["user_id"])})
    if not user:
        raise HTTPException(401, "User not found")

    # Rotate refresh token — revoke old, issue new
    await refresh_tokens_col.update_one(
        {"_id": record["_id"]}, {"$set": {"revoked": True}}
    )
    new_refresh = make_refresh_token()
    await save_refresh_token(record["user_id"], new_refresh)

    return {
        "access_token":  make_access_token(record["user_id"], user["email"]),
        "refresh_token": new_refresh,
        "expires_in":    ACCESS_EXP,
    }


@router.post("/logout")
async def logout(body: RefreshBody):
    """Revoke refresh token on sign-out."""
    await refresh_tokens_col.update_one(
        {"token": body.refresh_token},
        {"$set": {"revoked": True}}
    )
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(user=Depends(get_current_user_dep)):
    """Return full user profile — used by frontend on load."""
    return {
        "id":          str(user["_id"]),
        "email":       user["email"],
        "name":        user["name"],
        "phone":       user.get("phone"),
        "location":    user.get("location"),
        "plan":        user.get("plan", "free"),
        "login_count": user.get("login_count", 1),
        "created_at":  user.get("created_at", "").isoformat()
                       if user.get("created_at") else None,
    }


@router.patch("/profile")
async def update_profile(body: UpdateProfileBody, user=Depends(get_current_user_dep)):
    """Update name, phone, location."""
    updates = {k: v for k, v in body.dict().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    await users_col.update_one(
        {"_id": user["_id"]}, {"$set": updates}
    )
    return {"message": "Profile updated", "updated": updates}