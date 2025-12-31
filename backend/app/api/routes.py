from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/hello")
def say_hello() -> JSONResponse:
    return JSONResponse(content={"message": "Hello from FastAPI!"})
