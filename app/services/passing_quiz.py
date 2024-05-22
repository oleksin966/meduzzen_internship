from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from db.models import Company, Question, Quiz, QuizResult
from typing import List, Dict
from schemas.user_schema import UserId
from utils.utils import Paginate, calc_frequency_days, calc_score
from utils.exceptions import (QuizNotFound,   
    CompanyNotFoundException,   
    QuizNotBelongsToCompany,
    RemainingDays)
from datetime import datetime, timedelta

class PassingQuizService:
    def __init__(
        self, 
        session: AsyncSession, 
        user: UserId
    ):
        self.session = session
        self.user = user

    async def quiz(self, quiz_id: int):
        quiz = await self.session.get(
            Quiz, 
            quiz_id,
            options=[joinedload(Quiz.questions).joinedload(Question.options)]
        )
        if quiz is None:
            raise QuizNotFound()
        return quiz

    async def passing_quiz(self, company_id: int, quiz_id: int, data: Dict):
        # check if exist company
        company = await self.session.get(Company, company_id)
        if company_id != company.id: 
            raise CompanyNotFoundException()

        # check if exist quiz
        quiz = await self.session.get(
            Quiz, 
            quiz_id,
            options=[joinedload(Quiz.questions).joinedload(Question.options),
            joinedload(Quiz.company)]
        )
        if quiz is None:
            raise QuizNotFound()

        # check if quiz belong to this company
        if quiz.company_id != company_id:
            raise QuizNotBelongsToCompany()


        # check is user has already pass this quiz
        quiz_result = await self.session.execute(
            select(QuizResult) \
            .options(joinedload(QuizResult.quiz)) \
            .where((QuizResult.user_id == self.user.id) &
                (QuizResult.quiz_id == quiz_id))
        )
        quiz_result = quiz_result.scalar_one_or_none()
        if quiz_result is not None:
            remaining_days = calc_frequency_days(quiz_result.timestamp, quiz_result.quiz.frequency_days)
            # Calculate the remaining days until the quiz can be retaken
            if remaining_days > 0:
                raise RemainingDays(remaining_days)


        score_count = 0

        for question in quiz.questions:
            for answer in data:
                answer = answer.dict()
                if question.id == answer["question_id"]:
                    score_count += sum(answer["asnwer_id"] == option.id and option.is_correct for option in question.options)


        quiz_result = QuizResult(
            user_id=self.user.id,
            quiz_id=quiz_id,
            company_id=company_id,
            score=score_count
        )

        self.session.add(quiz_result)
        await self.session.commit()
        return quiz_result

    async def avarage_score(self, company_id: int):
        # get rating from choosed company
        user_results = await self.session.execute(
            select(QuizResult) \
            .options(joinedload(QuizResult.quiz).joinedload(Quiz.questions)) \
            .where((QuizResult.user_id == self.user.id) &
                (QuizResult.company_id == company_id))
        )

        user_results = user_results.unique().scalars().all()

        if not user_results:
            return 0

        if len(user_results) == 1:
            result = user_results[0]
            return round((result.score / len(result.quiz.questions)) * 100, 1)

        # according to the algorithm, we calculate the user's score in company 
        return calc_score(user_results)



    async def rating(self):
        # get rating from choosed company
        user_results = await self.session.execute(
            select(QuizResult) \
            .options(joinedload(QuizResult.quiz).joinedload(Quiz.questions)) \
            .where((QuizResult.user_id == self.user.id))
        )

        user_results = user_results.unique().scalars().all()

        if not user_results:
            return 0

        if len(user_results) == 1:
            result = user_results[0]
            return round((result.score / len(result.quiz.questions)) * 100, 1)

        # according to the algorithm, we calculate the rating in system
        return calc_score(user_results)


