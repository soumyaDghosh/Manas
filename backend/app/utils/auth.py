import logging
from logging import Logger
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from firebase_admin.auth import (
    CertificateFetchError,
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
    UserDisabledError,
)

security = HTTPBearer()
logger: Logger = logging.getLogger(__name__)


def verify_firebase_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except CertificateFetchError:
        logger.exception("error while fetching the public key certificates")
        raise HTTPException(status_code=500, detail="internal server error")
    except ExpiredIdTokenError:
        raise HTTPException(status_code=403, detail="id token expired")
    except RevokedIdTokenError:
        raise HTTPException(status_code=410, detail="id token revoked")
    except InvalidIdTokenError:
        raise HTTPException(status_code=404, detail="id token invalid")
    except UserDisabledError:
        raise HTTPException(status_code=403, detail="user is disabled")
    except Exception:
        logger.exception("unknown error")
        raise HTTPException(status_code=500, detail="internal server error")
