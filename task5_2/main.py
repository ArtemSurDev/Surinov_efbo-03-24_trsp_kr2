from fastapi import FastAPI, HTTPException, Response, Cookie
from pydantic import BaseModel
import uuid
from itsdangerous import URLSafeSerializer
from typing import Optional
import os

app = FastAPI(title="Task 5.2 - Signed Cookie Authentication")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
serializer = URLSafeSerializer(SECRET_KEY)

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

    session_token = serializer.dumps(user["user_id"])
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600, secure=False,
                        samesite="lax")
    return {"message": "Login successful"}


@app.get("/profile")
async def get_profile(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_id = serializer.loads(session_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid session token")

    for uname, data in users_db.items():
        if data["user_id"] == user_id:
            return {"username": uname, "name": data["name"], "email": data["email"], "user_id": user_id}

    raise HTTPException(status_code=401, detail="User not found")


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Logout successful"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)