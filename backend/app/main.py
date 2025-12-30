from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app import api
from app.config.settings import settings
from app.utils.redis import RedisService
from firebase_admin import credentials, firestore
from loguru import logger
import firebase_admin
import tempfile

with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
    temp_file.write(settings.FIREBASE_CREDENTIALS)
    temp_file_path = temp_file.name

cred = credentials.Certificate(temp_file_path)
firebase_admin.initialize_app(cred)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis_service = RedisService()
    app.state.firestore_db = firestore.client()
    logger.info("server started")
    yield
    app.state.redis_service.close()
    logger.info("shutting down")


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

for router in api.__all__:
    app.include_router(getattr(api, router), prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": "Mood analyzer API is running!"}
