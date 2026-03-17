from fastapi import FastAPI, HTTPException, Response, Header
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re

app = FastAPI(title="Task 5.5 - Common Headers Model")


class CommonHeaders(BaseModel):
    user_agent: str = Field(alias="User-Agent")
    accept_language: str = Field(alias="Accept-Language")

    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if not v:
            raise ValueError('Accept-Language header is required')
        pattern = r'^[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?(?:,[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?)*$'
        if not re.match(pattern, v):
            raise ValueError('Accept-Language header has invalid format')
        return v

    class Config:
        populate_by_name = True


@app.get("/headers")
async def get_headers(headers: CommonHeaders = Header()):
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}


@app.get("/info")
async def get_info(response: Response, headers: CommonHeaders = Header()):
    current_time = datetime.now().isoformat(timespec='seconds')
    response.headers["X-Server-Time"] = current_time
    return {"message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
            "headers": {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)