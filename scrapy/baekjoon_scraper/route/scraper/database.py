from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from connection.postgre import engine

def upsert_user_sequence(engine, user_id, problem_sequence):
    table_name = "user_sequence"
    table = Table(table_name, MetaData(), autoload_with=engine)
    stmt = insert(table).values(user_id=user_id, problem_sequence=problem_sequence)

    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['user_id'],  # user_id가 Primary Key라고 가정
        set_={'problem_sequence': problem_sequence}
    )

    with engine.connect() as conn:
        conn.execute(do_update_stmt)
        conn.commit()