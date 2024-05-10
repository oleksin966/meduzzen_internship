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

class NotPermission(Exception):
    def __init__(self):
        super().__init__("You do not have permission to add questions to this quiz.")




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




class QuizNotFound(Exception):
    def __init__(self):
        super().__init__("Quiz not found.")

class QuestionNotFound(Exception):
    def __init__(self):
        super().__init__("Question not found.")

class AnswerNotFound(Exception):
    def __init__(self):
        super().__init__("Answer not found.")

class ValuesError(Exception):
    def __init__(self):
        super().__init__("Values Error.")

class HasAlreadyAnswers(Exception):
    def __init__(self):
        super().__init__("This question have already answers.")

class QuizNotBelongsToCompany(Exception):
    def __init__(self):
        super().__init__("This Quiz dont belong to this company.")


