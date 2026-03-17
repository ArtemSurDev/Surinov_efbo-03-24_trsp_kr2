from fastapi import FastAPI
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

app = FastAPI(title="Task 3.1 - User Creation")

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(...)
    age: Optional[int] = Field(None, ge=0, le=150)
    is_subscribed: Optional[bool] = Field(False)

    @validator('email')
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError('Неверный формат email')
        return v

@app.post("/create_user", response_model=UserCreate)
async def create_user(user: UserCreate):
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)