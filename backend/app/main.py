from fastapi import FastAPI
from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router


app = FastAPI(
    title="Frugal AI Cost Intelligence",
    version="0.1.0",
    description="AI gateway for LLM cost optimization and observability.",
)

app.include_router(chat_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {
        "service": "Frugal AI Gateway",
        "status": "running",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }