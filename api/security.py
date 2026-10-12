import hmac
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer_scheme = HTTPBearer(auto_error=False)


def require_write_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
) -> None:
    expected_token = os.getenv("API_WRITE_TOKEN")
    if not expected_token or not expected_token.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Write access is not configured.",
        )
    if credentials is None or not hmac.compare_digest(
        credentials.credentials.encode("utf-8"),
        expected_token.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
