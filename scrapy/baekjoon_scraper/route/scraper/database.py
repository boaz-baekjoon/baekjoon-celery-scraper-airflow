from sqlalchemy import create_engine, Table, MetaData, text, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from connection.postgre import engine
from sqlalchemy.orm import sessionmaker
import logging


def upsert_user_sequence(user_id, problem_sequence, db_engine=engine) -> bool:
    table_name = "user_sequence"
    table = Table(table_name, MetaData(), autoload_with=db_engine)
    stmt = insert(table).values(user_id=user_id, problem_sequence=problem_sequence)

    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['user_id'],  # user_id가 Primary Key라고 가정
        set_={'problem_sequence': problem_sequence}
    )

    with db_engine.connect() as conn:
        conn.execute(do_update_stmt)
        conn.commit()

    return True


def get_user_id(db_engine=engine):
    """Fetches user_id and user_rank from the database."""
    try:
        Session = sessionmaker(bind=db_engine)
        session = Session()

        metadata = MetaData()
        metadata.reflect(engine)
        users_table = metadata.tables['users']

        # Query the database for user_id and user_rank, sorting by user_rank
        query = session.query(
            users_table.c.user_id,
            users_table.c.user_rank
        ).order_by(users_table.c.user_id.desc())

        user_info = [
            {'user_id': row.user_id, 'user_rank': row.user_rank}
            for row in query.all()
        ]

        return user_info

    except Exception as e:
        logging.error(f"Database query error: {e}")
        return []

    finally:
        session.close()
        engine.dispose()
