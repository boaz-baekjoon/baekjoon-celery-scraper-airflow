from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserDetails(Base):
    __tablename__ = 'user_details'
    __bind_key__ = 'baekjoon'

    user_id = Column(String, primary_key=True)
    user_tier = Column(Integer, primary_key=True)
    user_answer_num = Column(Integer)
    user_class = Column(Integer)
    user_joined_at = Column(String)
    user_max_streak = Column(Integer)
    user_rank = Column(Integer)
    user_rating = Column(Integer)
    user_rating_by_class = Column(Integer)
    user_rating_by_problems_sum = Column(Integer)
    user_rating_by_solved_count = Column(Integer)
    user_rating_by_vote_count = Column(Integer)


class UserResults(Base):
    __tablename__ = 'user_results'
    __bind_key__ = 'baekjoon'

    user_id = Column(String, primary_key=True)
    correct_answer = Column(String)
    answer_not_perfect = Column(String)
    try_not_correct = Column(String)


class UserSequence(Base):
    __tablename__ = 'user_sequence'
    __bind_key__ = 'baekjoon'

    user_id = Column(String, primary_key=True)
    problem_sequence = Column(String)


class Users(Base):
    __tablename__ = 'users'
    __bind_key__ = 'baekjoon'

    user_id = Column(String, primary_key=True)
    status_message = Column(String)
    user_answer_num = Column(Integer)
    user_answer_rate = Column(Float)
    user_rank = Column(Integer)
    user_submit_num = Column(Integer)
