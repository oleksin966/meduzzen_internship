from fastapi import APIRouter, Depends, HTTPException, Path
from services.passing_quiz import PassingQuizService
from db.database import get_async_session
from utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_schema import UserId
from schemas.quiz_schema import FullQuiz, AnswersBase, SendQuizResult, QuizResult, QuizScore
from utils.exceptions import (QuizNotFound, 
    QuizNotBelongsToCompany, 
    CompanyNotFoundException,
    RemainingDays)
from typing import List


router_passing_quiz = APIRouter(prefix="/quiz", tags=["Passing Quiz"])

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
    except RemainingDays as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router_passing_quiz.get('/avarage_score/{company_id}', summary="Get user's avarage score in company", response_model=QuizScore)
async def avarage_score(
        company_id: int = Path(..., title="The ID of quiz"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    passing_quiz = PassingQuizService(session, user)
    result = await passing_quiz.avarage_score(company_id)
    return QuizScore(score=result)

@router_passing_quiz.get('/rating', summary="Get user's rating from all system", response_model=QuizScore)
async def rating(
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    passing_quiz = PassingQuizService(session, user)
    result = await passing_quiz.rating()
    return QuizScore(score=result)
