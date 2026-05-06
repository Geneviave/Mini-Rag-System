from fastapi import FastAPI
from helpers.config import get_settings
from routes import router

app = FastAPI()
settings = get_settings()
app.include_router(router)

@app.get("/")
async def root():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }