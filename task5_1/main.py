from fastapi import FastAPI, HTTPException, Response, Cookie
from pydantic import BaseModel
import uuid
from typing import Optional

app = FastAPI(title="Task 5.1 - Cookie Authentication")

users_db = {
    "user123": {"password": "password123", "name": "John Doe", "email": "john@example.com"}
}

sessions = {}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(response: Response, login_data: LoginRequest):
    user = users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_token = str(uuid.uuid4())
    sessions[session_token] = login_data.username

    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600, secure=False,
                        samesite="lax")
    return {"message": "Login successful"}


@app.get("/user")
async def get_user_profile(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")

    username = sessions[session_token]
    user = users_db[username]
    return {"username": username, "name": user["name"], "email": user["email"]}


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Logout successful"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)