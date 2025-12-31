from .routes import router as test_router
from .session import router as session_router
from .user_profile import router as profile_router

__all__ = [
    "profile_router",
    "session_router",
    "test_router",
]
