from fastapi import status

class UnauthorizedException(Exception):
    def __init__(self, detail: str):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)

class UnauthenticatedException(Exception):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication")
