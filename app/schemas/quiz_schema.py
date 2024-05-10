from pydantic import BaseModel, Field
from typing import Optional, List
from schemas.user_schema import UserUsername, UserSchema
from datetime import datetime

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    frequency_days: Optional[int] = None

class QuizUpdate(QuizBase):
    title: Optional[str] = None
    description: Optional[str] = None
    frequency_days: Optional[int] = None

class QuizSchema(QuizBase):
    id: int
    company_id: int

class QuizId(QuizBase):
    id: int



class QuestionBase(BaseModel):
    question_text: str

class QuestionSchema(QuestionBase):
    id: int
    quiz_id: int

class QuestionUpdate(QuestionBase):
    question_text: Optional[str] = None



class AnswersBase(BaseModel):
    answer_text: str
    is_correct: bool

class AnswerSchema(AnswersBase):
    id: int
    question_id: int

class AnswerSchemaId(AnswersBase):
    id: int


class AnswerUpdate(AnswersBase):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    


class QuestionId(BaseModel):
    id: int
    question_text: str
    options: List[AnswerSchemaId]

class FullQuiz(BaseModel):
    id: int
    title: str
    questions: List[QuestionId]


class SendQuizResult(BaseModel):
    question_id: int
    asnwer_id: int


class QuizResult(BaseModel):
    id: int
    score: int
    timestamp: datetime

