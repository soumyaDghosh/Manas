from pydantic import BaseModel, Field
from datetime import datetime
from app.models.enums import MoodCategory
import re

class SessionModel(BaseModel):
    """
    Model for a user session stored in Firestore.
    """
    mood: MoodCategory
    summary: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    @classmethod
    def parse_json_markdown(cls, s: str):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.MULTILINE)
        return cls.model_validate_json(cleaned)

class SessionsResponse(BaseModel):
    """
    Response model for retrieving multiple sessions.
    """
    sessions: list[SessionModel]

