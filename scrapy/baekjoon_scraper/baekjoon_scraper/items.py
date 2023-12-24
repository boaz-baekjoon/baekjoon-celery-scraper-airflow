# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from collections import OrderedDict
import scrapy


class ProblemItem(scrapy.Item):
    problem_id = scrapy.Field()
    problem_title = scrapy.Field()
    problem_info = scrapy.Field()
    problem_answer_num = scrapy.Field()
    problem_submit_num = scrapy.Field()
    problem_answer_rate = scrapy.Field()


class UserItem(scrapy.Item):
    user_rank = scrapy.Field()
    user_id = scrapy.Field()
    status_message = scrapy.Field()
    user_answer_num = scrapy.Field()
    user_submit_num = scrapy.Field()
    user_answer_rate = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super(UserItem, self).__init__(*args, **kwargs)
        self._values = OrderedDict()


class WorkbookItem(scrapy.Item):
    workbook_rank = scrapy.Field()
    workbook_id = scrapy.Field()
    user_id = scrapy.Field()
    workbook_title = scrapy.Field()
    problem_id = scrapy.Field()
    problem_title = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super(WorkbookItem, self).__init__(*args, **kwargs)
        self._values = OrderedDict()


class ProblemDetailItem(scrapy.Item):
    problem_id = scrapy.Field()
    problem_title = scrapy.Field()
    problem_lang = scrapy.Field()
    tag_display_lang = scrapy.Field()
    tag_name = scrapy.Field()
    problem_titles_is_original = scrapy.Field()
    problem_is_solvable = scrapy.Field()
    problem_is_partial = scrapy.Field()
    problem_answer_num = scrapy.Field()
    problem_level = scrapy.Field()
    problem_voted_user_count = scrapy.Field()
    problem_sprout = scrapy.Field()
    problem_gives_no_rating = scrapy.Field()
    problem_is_level_locked = scrapy.Field()
    problem_average_tries = scrapy.Field()
    problem_official = scrapy.Field()
    tag_key = scrapy.Field()


class ProblemTextItem(scrapy.Item):
    problem_id = scrapy.Field()
    problem_title = scrapy.Field()
    problem_text = scrapy.Field()
    problem_input = scrapy.Field()
    problem_output = scrapy.Field()


class UserDetailItem(scrapy.Item):
    user_id = scrapy.Field()
    user_answer_num = scrapy.Field()
    user_tier = scrapy.Field()
    user_rating = scrapy.Field()
    user_rating_by_problems_sum = scrapy.Field()
    user_rating_by_class = scrapy.Field()
    user_rating_by_solved_count = scrapy.Field()
    user_rating_by_vote_count = scrapy.Field()
    user_class = scrapy.Field()
    user_max_streak = scrapy.Field()
    user_joined_at = scrapy.Field()
    user_rank = scrapy.Field()


class UserResultItem(scrapy.Item):
    user_id = scrapy.Field()
    correct_answer = scrapy.Field()
    answer_not_perfect = scrapy.Field()
    try_not_correct = scrapy.Field()