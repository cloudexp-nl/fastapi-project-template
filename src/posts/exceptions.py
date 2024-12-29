from fastapi import HTTPException, status
from .constants import POST_NOT_FOUND_MSG, UNAUTHORIZED_MSG

class PostNotFoundError(HTTPException):
    def __init__(self, detail: str = POST_NOT_FOUND_MSG):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class UnauthorizedPostAccessError(HTTPException):
    def __init__(self, detail: str = UNAUTHORIZED_MSG):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        ) 