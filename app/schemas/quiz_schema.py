from pydantic import BaseModel, Field
from typing import Optional, List
from schemas.user_schema import UserUsername, UserSchema

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    frequency_days: Optional[int] = None

class QuizUpdate(QuizBase):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency_days: Optional[int] = None


class QuestionBase(BaseModel):
    question_text: str

class QuestionSchema(QuestionBase):
    quiz_id: int

class QuestionUpdate(QuestionBase):
    question_text: Optional[str] = None


class AnswersBase(BaseModel):
    answer_text: str
    is_correct: bool

class AnswerSchema(AnswersBase):
    question_id: int

class AnswerUpdate(AnswersBase):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    

