import logging
from datetime import datetime
from logging import Logger
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import auth
from firebase_admin.auth import UserNotFoundError
from firebase_admin.exceptions import FirebaseError

from app.models.user_profile import Profile
from app.utils.auth import verify_firebase_token

router = APIRouter()

logger: Logger = logging.getLogger(__name__)


@router.get("/profile", response_model=Profile)
def get_profile(uid: Annotated[str, Depends(verify_firebase_token)]) -> Profile:
    """
    Get user profile information from Firebase Auth.

    Args:
        uid: User ID extracted from Firebase token

    Returns:
        Profile: User profile information

    Raises:
        HTTPException: 400 for malformed request, 502 for firebase error, 404 if user not found, 500 for other errors
    """
    try:
        user = auth.get_user(uid)
        return Profile(
            uid=uid,
            email=user.email or "",
            full_name=user.display_name or "",
            created_at=datetime.fromtimestamp(
                user.user_metadata.creation_timestamp / 1000
            ),
            updated_at=(
                datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000)
                if user.user_metadata.last_sign_in_timestamp
                else None
            ),
        )

    except UserNotFoundError:
        logger.warning(f"user with {uid} not found")
        raise HTTPException(status_code=404, detail="user not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="user id is malformed")
    except FirebaseError:
        logger.exception(f"firebase error for user {uid}")
        raise HTTPException(status_code=400, detail="failed to retrieve the user")
    except Exception:
        logger.exception(f"internal error for {uid}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/profile/display-name", response_model=Profile)
def set_display_name(
    display_name: str, uid: Annotated[str, Depends(verify_firebase_token)]
) -> Profile:
    """
    Update the user's display name in Firebase Auth.

    Args:
        display_name: New display name for the user
        uid: User ID extracted from Firebase token

    Returns:
        Profile: Updated user profile information

    Raises:
        HTTPException: 400 for invalid input, 502 for firebase error, 500 for other errors
    """
    if not display_name or len(display_name) not in range(3, 100):
        raise HTTPException(
            status_code=400, detail="Display name must be between 3 and 100 characters"
        )

    try:
        user = auth.update_user(uid, display_name=display_name)
        profile = Profile(
            uid=uid,
            email=user.email or "",
            full_name=user.display_name or "",
            created_at=datetime.fromtimestamp(
                user.user_metadata.creation_timestamp / 1000
            ),
            updated_at=(
                datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000)
                if user.user_metadata.last_sign_in_timestamp
                else None
            ),
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="invalid user id or name")
    except FirebaseError:
        logger.exception(f"firebase error for user {uid}")
        raise HTTPException(status_code=502, detail="failed to update the user account")
    except Exception:
        logger.exception(f"internal error for {uid}")
        raise HTTPException(status_code=500, detail="internal server error")
    else:
        logger.info(f"profile updated for {uid}: result {profile}")
        return profile
