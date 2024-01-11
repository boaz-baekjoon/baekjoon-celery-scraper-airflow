create table user_results
(
    user_id            varchar(255) not null
        primary key,
    correct_answer     text,
    answer_not_perfect text,
    try_not_correct    text
);

create index ix_user_results_user_id
    on user_results (user_id);


create table user_details
(
    user_id                     text   not null,
    user_tier                   bigint not null,
    user_answer_num             bigint,
    user_class                  bigint,
    user_joined_at              text,
    user_max_streak             bigint,
    user_rank                   bigint,
    user_rating                 bigint,
    user_rating_by_class        bigint,
    user_rating_by_problems_sum bigint,
    user_rating_by_solved_count bigint,
    user_rating_by_vote_count   bigint,
    primary key (user_id, user_tier)
);

alter table user_details
    owner to boaz;

create index ix_user_details_user_tier
    on user_details (user_tier);

create index ix_user_details_user_id
    on user_details (user_id);



