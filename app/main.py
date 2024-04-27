from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routers.health_check import router
from routers.connect_check import router_connects
from routers.user_route import router_user
from routers.auth_route import router_auth
from core.config import settings
from starlette.middleware.sessions import SessionMiddleware



from core.logging import LOGGING
from logging import getLogger

logger = getLogger(__name__)

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="add any string...")



# app.include_router(router)
# app.include_router(router_connects)
# app.include_router(router_user)
app.include_router(router_auth)


def run():
    if settings.environment == "development":
        import uvicorn
        uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload, log_config=LOGGING)
    else:
        pass
        
if __name__ == "__main__":
    run()
