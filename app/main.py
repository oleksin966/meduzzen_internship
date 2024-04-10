from fastapi import FastAPI
from .routers.health_check import router
from .core.config import settings

app = FastAPI()

app.include_router(router)

def run():
    if settings.environment == "development":
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        pass

if __name__ == "__main__":
    run()
