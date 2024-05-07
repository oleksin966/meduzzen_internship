from fastapi import status

class UnauthorizedException(Exception):
    def __init__(self, detail: str):
        super().__init__(status.HTTP_403_FORBIDDEN, detail)

class UnauthenticatedException(Exception):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication")


class UserNotFoundException(Exception):
    def __init__(self):
        super().__init__("User not found.")


class CompanyNotFoundException(Exception):
    def __init__(self):
        super().__init__("Company not found.")

class AlreadyMemberException(Exception):
    def __init__(self):
        super().__init__("The user is already a member of this company.")

class NotOwnerCompanyException(Exception):
    def __init__(self):
        super().__init__("You are not the owner of this company")



class InvitationOwnershipException(Exception):
    def __init__(self):
        super().__init__("This invitation not for you")

class InvitationAlreadySentException(Exception):
    def __init__(self):
        super().__init__("An invitation has already been sent to this user for this company.")

class InvitationNotFoundException(Exception):
    def __init__(self):
        super().__init__("Invitation not found.")




class RequestNotFoundException(Exception):
    def __init__(self):
        super().__init__("Request not found.")

class RequestAlreadySentException(Exception):
    def __init__(self):
        super().__init__("An request has already been sent to this user for this company.")

class RequestOwnershipException(Exception):
    def __init__(self):
        super().__init__("This request not your.")

