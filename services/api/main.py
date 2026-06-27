from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine
from routers.auth import router as auth_router
from routers.debates import router as debates_router
from routers.dify import router as dify_router
from routers.friend_ai import router as friend_ai_router
from routers.graph import router as graph_router
from routers.im import router as im_router
from routers.market import router as market_router
from routers.mini_programs import router as mini_programs_router
from routers.notes import router as notes_router
from routers.profile import router as profile_router
from routers.search import router as search_router
from routers.social import router as social_router
from routers.tasks import router as tasks_router
from routers.workspace import router as workspace_router
from security import decode_access_token


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

@app.middleware("http")
async def jwt_state_middleware(request, call_next):
    request.state.user_id = None
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token:
        try:
            request.state.user_id = decode_access_token(token)["sub"]
        except ValueError:
            request.state.user_id = None
    return await call_next(request)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(debates_router, prefix="/api/v1")
app.include_router(dify_router, prefix="/api/v1")
app.include_router(friend_ai_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(im_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(mini_programs_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(social_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(workspace_router, prefix="/api/v1")
app.include_router(notes_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "metagpt_x_api": settings.metagpt_x_api}


@app.get("/api/v1/stack")
async def stack_info():
    return {
        "project": "zhixing",
        "phase": "P0",
        "metagpt_root": settings.metagpt_root,
        "metagpt_x_api": settings.metagpt_x_api,
    }
