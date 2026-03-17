from fastapi import FastAPI, HTTPException, Response, Cookie
from pydantic import BaseModel
import uuid
import time
import hmac
import hashlib
import os
from typing import Optional

app = FastAPI(title="Task 5.3 - Session with Expiration")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production").encode()


def create_signature(user_id: str, timestamp: int) -> str:
    message = f"{user_id}.{timestamp}".encode()
    return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()


def verify_signature(user_id: str, timestamp: int, signature: str) -> bool:
    expected = create_signature(user_id, timestamp)
    return hmac.compare_digest(expected, signature)


def create_session_token(user_id: str, timestamp: int) -> str:
    signature = create_signature(user_id, timestamp)
    return f"{user_id}.{timestamp}.{signature}"


def parse_session_token(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        user_id, timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        if not verify_signature(user_id, timestamp, signature):
            raise ValueError("Invalid signature")
        return user_id, timestamp
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid session")


users_db = {
    "user123": {"password": "password123", "name": "John Doe", "email": "john@example.com",
                "user_id": str(uuid.uuid4())}
}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(response: Response, login_data: LoginRequest):
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    current_time = int(time.time())
    session_token = create_session_token(user["user_id"], current_time)
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=300, secure=False,
                        samesite="lax")
    return {"message": "Login successful", "timestamp": current_time}


@app.get("/profile")
async def get_profile(response: Response, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Session expired")

    try:
        user_id, last_activity = parse_session_token(session_token)
    except HTTPException:
        raise

    current_time = int(time.time())
    time_diff = current_time - last_activity

    if time_diff > 300:
        response.delete_cookie("session_token")
        raise HTTPException(status_code=401, detail="Session expired")

    user_profile = None
    username = None
    for uname, data in users_db.items():
        if data["user_id"] == user_id:
            user_profile = data
            username = uname
            break

    if not user_profile:
        raise HTTPException(status_code=401, detail="User not found")

    if 180 <= time_diff < 300:
        new_session_token = create_session_token(user_id, current_time)
        response.set_cookie(key="session_token", value=new_session_token, httponly=True, max_age=300, secure=False,
                            samesite="lax")

    return {"username": username, "name": user_profile["name"], "email": user_profile["email"],
            "last_activity": last_activity, "current_time": current_time, "time_diff": time_diff}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)