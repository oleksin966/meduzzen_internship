from fastapi import FastAPI
from .routers.health_check import router

app = FastAPI()

app.include_router(router)