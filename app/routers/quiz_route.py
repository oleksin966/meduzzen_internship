from fastapi import APIRouter, Depends, HTTPException, Path
from db.database import get_async_session
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserId
from schemas.quiz_schema import (QuizBase, 
    AnswersBase, 
    QuizUpdate, 
    QuestionSchema, 
    QuestionUpdate,
    AnswerUpdate)
from services.quiz_service import QuizService
from utils.exceptions import (QuizNotFound, 
    NotPermission, 
    QuestionNotFound, 
    ValuesError, 
    AnswerNotFound, 
    HasAlreadyAnswers,
    CompanyNotFoundException)
from typing import List


router_quiz = APIRouter(prefix="/quiz", tags=["Quizzes"])




# GET QUIZZES
@router_quiz.get('/all', summary="Get all quizzes", response_model=List[QuizBase])
async def all_quizzes(
    page: int = 1,
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    quiz_service = QuizService(session, user)
    return await quiz_service.all_quizzes(page)


@router_quiz.get('/{company_id}', summary="Get quizzes by company", response_model=List[QuizBase])
async def get_quizzes(
    page: int = 1,
    company_id: int = Path(..., title="The ID of company"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.get_quizzes(page, company_id)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found.")






# QUIZZES
@router_quiz.post('/create/{company_id}', summary="Create quiz", response_model=QuizBase)
async def create_quiz(
    quiz: QuizBase = Depends(),
    company_id: int = Path(..., title="The ID of company"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.create_quiz(company_id, quiz)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to create this quiz")

@router_quiz.put('/update/{quiz_id}', summary="Update quiz", response_model=QuizUpdate)
async def update_quiz(
    quiz: QuizUpdate = Depends(),
    quiz_id: int = Path(..., title="The ID of quiz"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.update_quiz(quiz_id, quiz)
    except QuizNotFound:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to update this quiz")

@router_quiz.delete('/delete/{quiz_id}', summary="Delete quiz", response_model=QuizBase)
async def delete_quiz(
    quiz_id: int = Path(..., title="The ID of quiz"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.delete_quiz(quiz_id)
    except QuizNotFound:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to update this quiz")







# QUESTIONS
@router_quiz.post('/question/{quiz_id}', summary="Create question", response_model=QuestionSchema)
async def create_question(
    question: QuestionSchema = Depends(),
    quiz_id: int = Path(..., title="The ID of question"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.create_question(quiz_id, question)
    except QuestionNotFound:
        raise HTTPException(status_code=404, detail="Question not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to add questions to this quiz")


@router_quiz.put('/question/update/{question_id}', summary="Update question", response_model=QuestionSchema)
async def update_questions(
    question: QuestionUpdate = Depends(),
    question_id: int = Path(..., title="The ID of question"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.update_questions(question_id, question)
    except QuizNotFound:
        raise HTTPException(status_code=404, detail="Question not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to update this questions")


@router_quiz.delete('/question/delete/{question_id}', summary="Delete question", response_model=QuestionSchema)
async def delete_questions(
    question_id: int = Path(..., title="The ID of question"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
    ):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.delete_questions(question_id)
    except QuizNotFound:
        raise HTTPException(status_code=404, detail="Question not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this questions")











# ANSWERS
@router_quiz.post("/answers/{question_id}", summary="Create answer", response_model=List[AnswersBase])
async def create_answers(
    answers: List[AnswersBase],
    question_id: int = Path(..., title="The ID of question"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.create_answers(question_id, answers)
    except QuestionNotFound:
        raise HTTPException(status_code=404, detail="Question not found.")
    except HasAlreadyAnswers:
        raise HTTPException(status_code=400, detail="This question has already answers.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to add answer to this question")
    except ValuesError:
        raise HTTPException(status_code=400, detail="At least two answers are required.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router_quiz.put("/answers/update/{answer_id}", summary="Update answer", response_model=AnswersBase)
async def update_answers(
    answer: AnswerUpdate = Depends(),
    answer_id: int = Path(..., title="The ID of answer"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.update_answers(answer_id, answer)
    except AnswerNotFound:
        raise HTTPException(status_code=404, detail="Answer not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to update this answer")



@router_quiz.delete("/answers/delete/{answer_id}", summary="Delete answer", response_model=AnswersBase)
async def delete_answers(
    answer_id: int = Path(..., title="The ID of answer"),
    session: AsyncSession = Depends(get_async_session),
    user: UserId = Depends(get_current_user)
):
    try:
        quiz_service = QuizService(session, user)
        return await quiz_service.delete_answers(answer_id)
    except AnswerNotFound:
        raise HTTPException(status_code=404, detail="Answer not found.")
    except NotPermission:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this answer")