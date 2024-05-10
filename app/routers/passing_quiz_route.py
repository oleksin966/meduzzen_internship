from fastapi import APIRouter, Depends, HTTPException, Path
from services.passing_quiz import PassingQuizService
from db.database import get_async_session
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserId
from schemas.quiz_schema import FullQuiz, AnswersBase, SendQuizResult, QuizResult
from utils.exceptions import (QuizNotFound, 
    QuizNotBelongsToCompany, 
    CompanyNotFoundException)
from typing import List


router_passing_quiz = APIRouter(prefix="/passing", tags=["Passing Quiz"])

@router_passing_quiz.get('/get/{quiz_id}', summary="Get quiz by id", response_model=FullQuiz)
async def quiz(
        quiz_id: int = Path(..., title="The ID of quiz"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    try:
        passing_quiz = PassingQuizService(session, user)
        return await passing_quiz.quiz(quiz_id)
    except QuizNotFound:
        raise HTTPException(status_code=404, detail="Quiz not found.")

@router_passing_quiz.post('/{quiz_id}', summary="Passing quiz", response_model=QuizResult)
async def passing_quiz(
        company_id: int,
        questions: List[SendQuizResult],
        quiz_id: int = Path(..., title="The ID of quiz"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    try:
        passing_quiz = PassingQuizService(session, user)
        return await passing_quiz.passing_quiz(company_id, quiz_id, questions)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found.")
    except QuizNotFound:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    except QuizNotBelongsToCompany:
        raise HTTPException(status_code=403, detail="Quiz not belong to this company.")


@router_passing_quiz.get('/rating/{company_id}', summary="Get user's Rating")
async def rating(
        company_id: int = Path(..., title="The ID of quiz"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    passing_quiz = PassingQuizService(session, user)
    result = await passing_quiz.rating(company_id)
    return {"Your rating":f"{result}%"}
