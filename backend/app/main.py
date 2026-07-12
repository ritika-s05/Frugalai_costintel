from fastapi import FastAPI

app = FastAPI(
    title="Frugal AI Gateway",
    version="1.0.0"
)
@app.get("/")
def root():
    return {
        "service": "Frugal AI Gateway",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }