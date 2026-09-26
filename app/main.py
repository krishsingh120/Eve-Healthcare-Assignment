from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import auth, centres, tests, bookings, payments

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(centres.router, prefix=f"{settings.API_V1_STR}/centres", tags=["centres"])
app.include_router(tests.router, prefix=f"{settings.API_V1_STR}/tests", tags=["tests"])
app.include_router(bookings.router, prefix=f"{settings.API_V1_STR}/bookings", tags=["bookings"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
