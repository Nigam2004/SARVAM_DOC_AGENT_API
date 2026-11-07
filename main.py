from fastapi import FastAPI
from src.sarvam_api_testing.api.routs import router

app = FastAPI(
    title="HR Gate Pass Agent",
    description="Sarvam document extraction API",
    version="1.0.0"
)

app.include_router(
    router,
    prefix="/api",
    tags=["Document Extraction"]
)


@app.get("/")
async def home():
    return {
        "message": "HR Gate Pass Agent is running"
    }