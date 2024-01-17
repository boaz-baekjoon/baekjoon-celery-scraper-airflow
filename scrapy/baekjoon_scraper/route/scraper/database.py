from sqlalchemy import select
from sqlalchemy.orm import Session
from connection.postgre import engines, RoutingSession
from models.model import UserSequence, Users

import logging


def upsert_user_sequence(user_id: str, problem_sequence: str) -> bool:
    try:
        db_engine = engines['baekjoon']
        with RoutingSession(bind=db_engine) as session:
            statement = select(UserSequence).where(UserSequence.user_id == user_id)
            result = session.execute(statement)
            user_sequence = result.scalars().first()

            if user_sequence:
                user_sequence.problem_sequence = problem_sequence
            else:
                new_user_sequence = UserSequence(user_id=user_id, problem_sequence=problem_sequence)
                session.add(new_user_sequence)

            session.commit()
        return True
    except Exception as e:
        logging.error(f"Database operation error: {e}")
        return False


def get_user_id(db_engine=None):
    if db_engine is None:
        db_engine = engines['baekjoon']

    try:
        with RoutingSession(bind=db_engine) as session:
            statement = select(Users.user_id, Users.user_rank).order_by(Users.user_id.desc())
            result = session.execute(statement)
            return [{'user_id': row.user_id, 'user_rank': row.user_rank} for row in result]
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return []


def get_user_info():
    try:
        db_engine = engines['baekjoon']
        with RoutingSession(bind=db_engine) as session:
            statement = select(Users.user_id, Users.user_rank).order_by(Users.user_rank)
            result = session.execute(statement)
            users = result.fetchall()
            return [{'user_id': user[0], 'user_rank': user[1]} for user in users]
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return []
