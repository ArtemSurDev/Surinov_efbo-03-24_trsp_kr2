from fastapi import FastAPI, HTTPException, Header
from typing import Optional
import re

app = FastAPI(title="Task 5.4 - Headers Processing")

def validate_accept_language(accept_language: str) -> bool:
    if not accept_language:
        return False
    pattern = r'^[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?(?:,[a-zA-Z-]+(?:;[a-zA-Z]=[0-9.]+)?)*$'
    return bool(re.match(pattern, accept_language))

@app.get("/headers")
async def get_headers(user_agent: Optional[str] = Header(None, alias="User-Agent"), accept_language: Optional[str] = Header(None, alias="Accept-Language")):
    if not user_agent:
        raise HTTPException(status_code=400, detail="User-Agent header is required")
    if not accept_language:
        raise HTTPException(status_code=400, detail="Accept-Language header is required")
    if not validate_accept_language(accept_language):
        raise HTTPException(status_code=400, detail="Accept-Language header has invalid format")
    return {"User-Agent": user_agent, "Accept-Language": accept_language}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)