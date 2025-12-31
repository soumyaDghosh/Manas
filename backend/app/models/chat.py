import re
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import MoodCategory


class ChatInput(BaseModel):
    """Model for chat input data."""

    text: str
    timestamp: datetime

    def __len__(self) -> int:
        return len(self.text)


class ConversationMessage(BaseModel):
    """Model for a single conversation message and response pair."""

    message: str
    reply: str
    timestamp: datetime


class MoodAnalysisResult(BaseModel):
    """Model for mood analysis result."""

    mood: MoodCategory = Field(..., description="Detected mood category")
    confidence: int = Field(..., ge=0, le=100, description="Confidence score 0-100")
    reply: str = Field(..., min_length=1, description="Generated empathetic reply")

    @classmethod
    def parse_json_markdown(cls, s: str) -> "MoodAnalysisResult":
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.MULTILINE)
        return cls.model_validate_json(cleaned)
