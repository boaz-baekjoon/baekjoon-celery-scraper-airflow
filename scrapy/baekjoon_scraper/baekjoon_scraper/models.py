from pydantic import BaseModel
from typing import Optional, List, Text


class ProblemModel(BaseModel):
    problem_id: int
    problem_title: Optional[str]
    problem_info: Optional[str]
    problem_answer_num: Optional[int]
    problem_submit_num: Optional[int]
    problem_answer_rate: Optional[float]


class UserModel(BaseModel):
    user_id: str
    status_message: Optional[str]
    user_answer_num: Optional[int]
    user_submit_num: Optional[int]
    user_answer_rate: Optional[float]
    user_rank: Optional[int]


class WorkbookModel(BaseModel):
    workbook_id: int
    problem_id: int
    user_id: Optional[str]
    workbook_rank: Optional[int]
    workbook_title: Optional[str]
    problem_title: Optional[str]


class ProblemDetailModel(BaseModel):
    problem_id: int
    problem_level: int
    tag_key: str
    problem_title: Optional[str]
    problem_lang: Optional[str]
    tag_display_lang: Optional[str]
    tag_name: Optional[str]
    problem_titles_is_original: Optional[bool]
    problem_is_solvable: Optional[bool]
    problem_is_partial: Optional[bool]
    problem_answer_num: Optional[int]
    problem_voted_user_count: Optional[int]
    problem_sprout: Optional[bool]
    problem_gives_no_rating: Optional[bool]
    problem_is_level_locked: Optional[bool]
    problem_average_tries: Optional[float]
    problem_official: Optional[bool]


class ProblemTextModel(BaseModel):
    problem_id: int
    problem_title: str
    problem_text: Optional[str]
    problem_input: Optional[str]
    problem_output: Optional[str]


class UserDetailModel(BaseModel):
    user_id: str
    user_tier: int
    user_answer_num: Optional[int]
    user_class: Optional[int]
    user_joined_at: Optional[str]
    user_max_streak: Optional[int]
    user_rank: Optional[int]
    user_rating: Optional[int]
    user_rating_by_class: Optional[int]
    user_rating_by_problems_sum: Optional[int]
    user_rating_by_solved_count: Optional[int]
    user_rating_by_vote_count: Optional[int]


class UserResultModel(BaseModel):
    user_id: str
    correct_answer: Optional[List[str]]
    answer_not_perfect: Optional[List[str]]
    try_not_correct: Optional[List[str]]