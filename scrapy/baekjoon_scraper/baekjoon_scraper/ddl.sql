CREATE TABLE IF NOT EXISTS user_results (
    user_id VARCHAR(255) NOT NULL,
    correct_answer TEXT[],
    answer_not_perfect TEXT[],
    try_not_correct TEXT[],
    PRIMARY KEY (user_id)
);