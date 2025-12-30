from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Profile(BaseModel):
    """
    Model for user profile information.
    """

    uid: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
