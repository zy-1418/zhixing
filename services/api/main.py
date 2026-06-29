from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine
from routers.auth import router as auth_router
from routers.dify import router as dify_router
from routers.extensions import compat_router as extensions_compat_router
from routers.extensions import router as extensions_router
from routers.notes import router as notes_router
from routers.social import debates_router, router as social_router
from routers.tasks import router as tasks_router
from routers.workspace import router as workspace_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(workspace_router, prefix="/api/v1")
app.include_router(notes_router, prefix="/api/v1")
app.include_router(dify_router, prefix="/api/v1")
app.include_router(social_router, prefix="/api/v1")
app.include_router(debates_router, prefix="/api/v1")
app.include_router(extensions_router, prefix="/api/v1")
app.include_router(extensions_compat_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "metagpt_x_api": settings.metagpt_x_api}


@app.get("/api/v1/stack")
async def stack_info():
    return {
        "project": "zhixing",
        "phase": "P4-skeleton",
        "metagpt_root": settings.metagpt_root,
        "metagpt_x_api": settings.metagpt_x_api,
        "dify_configured": bool(settings.dify_api_key),
    }
