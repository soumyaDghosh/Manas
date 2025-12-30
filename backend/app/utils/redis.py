from redis import Redis
from fastapi import Request
from app.config.settings import settings
from app.models.chat import ConversationMessage, MoodAnalysisResult
from typing import Awaitable
from loguru import logger


class RedisService:
    def __init__(self):
        self._redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
            password=settings.REDIS_PASSWORD,
            username=settings.REDIS_USERNAME,
        )
        logger.info("redis client initialized")

    @staticmethod
    def get_service(request: Request) -> Redis:
        return request.app.state.redis_service

    def clear_db(self, uid: str) -> None:
        self._redis_client.delete(
            f"user:{uid}:chat_history", f"user:{uid}:session_moods"
        )
        logger.info("cleared the db")

    def close(self):
        self._redis_client.close()
        logger.info("redis client closed")

    async def get_chat_history(self, user_id: str) -> list[ConversationMessage]:
        result: Awaitable[list] | list = self._redis_client.lrange(
            f"user:{user_id}:chat_history", 0, -1
        )
        if isinstance(result, Awaitable):
            result = await result

        return list(map(ConversationMessage.model_validate_json, result))

    async def add_chat_history(self, user_id: str, chat: ConversationMessage):
        self._redis_client.rpush(f"user:{user_id}:chat_history", chat.model_dump_json())
        logger.info("added chat history")

    async def add_session_moods(self, user_id: str, mood: MoodAnalysisResult):
        self._redis_client.rpush(
            f"user:{user_id}:session_moods", mood.model_dump_json()
        )
        logger.info("added session moods")

    async def get_session_moods(self, user_id: str) -> list[MoodAnalysisResult]:
        result = self._redis_client.lrange(f"user:{user_id}:session_moods", 0, -1)
        if isinstance(result, Awaitable):
            result = await result

        return list(map(MoodAnalysisResult.model_validate_json, result))
