from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from db.models import Company, Question, CompanyUser, Quiz, Answer
from typing import List, Dict
from schemas.user_schema import UserId
from schemas.quiz_schema import QuizBase, AnswersBase, QuestionSchema
from utils.utils import Paginate
from utils.decorators import check_if_user_or_owner
from utils.exceptions import (QuizNotFound, 
    NotPermission, 
    QuestionNotFound, 
    CompanyNotFoundException, 
    HasAlreadyAnswers, 
    ValuesError, 
    AnswerNotFound)

class QuizService:
    def __init__(
        self, 
        session: AsyncSession, 
        user: UserId
    ):
        self.session = session
        self.user = user


    async def all_quizzes(self, page: int) -> List[QuizBase]:
        '''Get all quizzes'''
        paginator = Paginate(self.session, Quiz, page)
        paginate_quiz = await paginator.fetch_results()
        return paginate_quiz


    async def get_quizzes(self, page: int, company_id: int) -> List[QuizBase]:
        '''Get quizzes by company'''
        company = await self.session.get(Company, company_id)
        if company is None:
            raise CompanyNotFoundException()

        where = Quiz.company_id == company_id
        paginator = Paginate(self.session, Quiz, page, where=where)
        paginate_quiz = await paginator.fetch_results()
        return paginate_quiz



    #CRUD QUIZ
    @check_if_user_or_owner # I JUST researched how custom decorator works with service
    async def create_quiz(self, company_id: int, quiz: Dict) -> QuizBase:
        '''Create quiz by company id. Decorator check if user or owner proccess creatinf quiz'''
        model_dump = quiz.dict()
        model_dump['company_id'] = company_id
        new_quiz = Quiz(**model_dump)
        
        self.session.add(new_quiz)
        await self.session.commit()
        await self.session.refresh(new_quiz)
        return new_quiz


    async def update_quiz(self, quiz_id: int, data: Dict) -> Quiz:
        data = data.dict(exclude_none=True)
        quiz = await self.session.get(
            Quiz, 
            quiz_id,
            options=[
                joinedload(Quiz.company).joinedload(Company.company_users)
            ]
        )
        if quiz is None:
            raise QuizNotFound()
            
        # check if user is admin or owner
        admin = None
        owner = quiz.company.owner_id == self.user.id
        for user in quiz.company.company_users:
            if user.user_id == self.user.id and user.is_administrator:
                admin = user
                break

        if not owner and not admin:
            raise NotPermission()

        statement = (
            update(Quiz)
            .where(Quiz.id == quiz_id)
            .values(data)
            .returning(Quiz)
        )
        updating = await self.session.execute(statement)
        updated_quiz = updating.scalar_one()
        
        await self.session.commit()
        await self.session.refresh(updated_quiz)
        return updated_quiz


    async def delete_quiz(self, quiz_id: int) -> Quiz:
        quiz = await self.session.get(
            Quiz, 
            quiz_id,
            options=[
                joinedload(Quiz.company).joinedload(Company.company_users)
            ]
        )
        if quiz is None:
            raise QuizNotFound()

        admin = None
        owner = quiz.company.owner_id == self.user.id
        for user in quiz.company.company_users:
            if user.user_id == self.user.id and user.is_administrator:
                admin = user
                break

        if not owner and not admin:
            raise NotPermission()

        await self.session.delete(quiz)
        await self.session.commit()
        return quiz






    #CRUD QUESTION
    async def create_question(self, quiz_id: int, question: QuestionSchema) -> QuestionSchema:
        quiz = await self.session.get(
            Quiz, 
            quiz_id,
            options=[
            joinedload(Quiz.company).joinedload(Company.company_users)])
        if quiz is None:
            raise QuizNotFound()

        admin = None
        owner = quiz.company.owner_id == self.user.id
        for user in quiz.company.company_users:
            if user.user_id==self.user.id and user.is_administrator == True:
                admin = user
                break

        if not owner and not admin:
            raise NotPermission()

        model_dump = question.dict()
        model_dump['quiz_id'] = quiz_id
        new_question = Question(**model_dump)
        
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question



    async def update_questions(self, question_id: int, data: Dict) -> Question:
        data = data.dict(exclude_none=True)
        question = await self.session.get(
            Question, 
            question_id,
            options=[
                joinedload(Question.quiz)
                .joinedload(Quiz.company)
                .joinedload(Company.company_users)
            ]
        )
        if question is None:
            raise QuizNotFound()

        owner = question.quiz.company.owner_id == self.user.id
        admin = None
        for user in question.quiz.company.company_users:
            if user.user_id==self.user.id and user.is_administrator == True:
                admin = user
                break

        if not owner and not admin:
            raise NotPermission()

        statement = (
            update(Question)
            .where(Question.id == question_id)
            .values(data)
            .returning(Question)
        )

        updating = await self.session.execute(statement)
        updated_question = updating.scalar_one()
        
        await self.session.commit()
        await self.session.refresh(updated_question)
        return updated_question



    async def delete_questions(self, question_id: int) -> Question:
        question = await self.session.get(
            Question, 
            question_id,
            options=[
                joinedload(Question.quiz)
                .joinedload(Quiz.company)
                .joinedload(Company.company_users)
            ]
        )
        if question is None:
            raise QuizNotFound()

        owner = question.quiz.company.owner_id == self.user.id
        admin = None
        for user in question.quiz.company.company_users:
            if user.user_id==self.user.id and user.is_administrator == True:
                admin = user
                break

        if not owner and not admin:
            raise NotPermission()

        await self.session.delete(question)
        await self.session.commit()
        return question










    #CRUD ANSWERS
    async def create_answers(self, question_id: int, answers: List[AnswersBase]) -> List[AnswersBase]:
        question = await self.session.get(
            Question, 
            question_id,
            options=[
                joinedload(Question.quiz)
                .joinedload(Quiz.company)
                .joinedload(Company.company_users),
                joinedload(Question.options)
            ]
        )

        if question is None:
            raise QuestionNotFound()

        if question.options != []:
            raise HasAlreadyAnswers()  

        owner = question.quiz.company.owner_id == self.user.id
        admin = None
        for user in question.quiz.company.company_users:
            if user.user_id==self.user.id and user.is_administrator == True:
                admin = user
            break

        if not owner and not admin:
            raise NotPermission()

        #check if answers less than 2
        if len(answers) < 2:
            raise ValuesError()

        correct = 0
        new_answers = []

        for answer_data in answers:
            model_dump = answer_data.dict()
            model_dump['question_id'] = question_id

            # check if ansvers has only one correct answer
            if model_dump['is_correct'] == True:
                correct += 1  
                if correct > 1:
                    raise ValueError("Only one correct answer is allowed")

            new_answer = Answer(**model_dump)
            self.session.add(new_answer)
            new_answers.append(new_answer)
        await self.session.commit()
        return new_answers        




    async def update_answers(self, answer_id: int, data: Dict) -> Answer:
        data = data.dict(exclude_none=True)
        answer = await self.session.get(
            Answer, 
            answer_id,
            options=[
                joinedload(Answer.question)
                .joinedload(Question.quiz)
                .joinedload(Quiz.company)
                .joinedload(Company.company_users)
            ]
        )
        if answer is None:
            raise AnswerNotFound()

        owner = answer.question.quiz.company.owner_id == self.user.id
        admin = None
        for user in answer.question.quiz.company.company_users:
            if user.user_id==self.user.id and user.is_administrator == True:
                admin = user
            break

        if not owner and not admin:
            raise NotPermission()

        statement = (
            update(Answer)
            .where(Answer.id == answer_id)
            .values(data)
            .returning(Answer)
        )

        updating = await self.session.execute(statement)
        updated_answer = updating.scalar_one()
        
        await self.session.commit()
        await self.session.refresh(updated_answer)
        return updated_answer


    async def delete_answers(self, answer_id: int) -> Answer:
        answer = await self.session.get(
            Answer, 
            answer_id,
            options=[
                joinedload(Answer.question)
                .joinedload(Question.quiz)
                .joinedload(Quiz.company)
                .joinedload(Company.company_users)
            ]
        )
        if answer is None:
            raise AnswerNotFound()

        owner = answer.question.quiz.company.owner_id == self.user.id
        admin = None
        for user in answer.question.quiz.company.company_users:
            if user.user_id==self.user.id and user.is_administrator == True:
                admin = user
            break

        if not owner and not admin:
            raise NotPermission()


        await self.session.delete(answer)
        await self.session.commit()
        return answer