from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
