"""
FastAPI main app.
"""
from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.config import PROJECT_SETTINGS, initialize_settings
from web import auth, product

initialize_settings()  # always run this first

app = FastAPI(
    title="FastAPI + SQLAlchemy 2.0 Demo Project",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(origin).strip("/") for origin in PROJECT_SETTINGS.CORS_ORIGINS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_router = APIRouter()
api_v1_router.include_router(
    product.router,
    prefix="/products",
    tags=["product"],
)
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])

app.include_router(api_v1_router, prefix=PROJECT_SETTINGS.API_V1_PATH)


@app.get("/")
async def root():
    return {"message": "FastAPI + SQLAlchemy 2.0 Demo Project"}
