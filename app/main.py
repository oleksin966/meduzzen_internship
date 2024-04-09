from fastapi import FastAPI
from routers import health_check

app = FastAPI()

app.include_router(health_check.router)