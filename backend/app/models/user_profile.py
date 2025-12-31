from datetime import datetime

from pydantic import BaseModel


class Profile(BaseModel):
    """
    Model for user profile information.
    """

    uid: str
    email: str
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
