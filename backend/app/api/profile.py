from fastapi import APIRouter, Depends, HTTPException
from app.models.profile import Profile
from app.utils.auth import verify_firebase_token
from firebase_admin import auth
from datetime import datetime, timezone

router = APIRouter()

@router.get("/profile", response_model=Profile)
def get_profile(uid: str = Depends(verify_firebase_token)):
    """
    Get user profile information from Firebase Auth.

    Args:
        uid: User ID extracted from Firebase token

    Returns:
        Profile: User profile information

    Raises:
        HTTPException: 404 if user not found, 500 for other errors
    """
    try:
        user = auth.get_user(uid)
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
            )
        )

        return profile

    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"User with UID {uid} not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing user data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/profile/display-name")
def set_display_name(
    display_name: str,
    uid: str = Depends(verify_firebase_token)
):
    """
    Update the user's display name in Firebase Auth.

    Args:
        display_name: New display name for the user
        uid: User ID extracted from Firebase token

    Returns:
        Profile: Updated user profile information

    Raises:
        HTTPException: 400 for invalid input, 404 if user not found, 500 for other errors
    """
    if not display_name or len(display_name) not in range(3, 100):
        raise HTTPException(
            status_code=400,
            detail="Display name must be between 3 and 100 characters"
        )

    try:
        auth.update_user(
            uid,
            display_name=display_name
        )
        return "Profile updated successfully"

    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"User with UID {uid} not found"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing user data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
