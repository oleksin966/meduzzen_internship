from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers.health_check import router
from routers.connect_check import router_connects
from core.config import settings

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "postgres://db:5432",
    "redis://redis:6379",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_connects)

def run():
    if settings.environment == "development":
        import uvicorn
        uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
    else:
        pass

if __name__ == "__main__":
    run()
