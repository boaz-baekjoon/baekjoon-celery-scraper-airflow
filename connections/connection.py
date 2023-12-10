import json
from airflow.models import Connection
from airflow.settings import Session
import logging

def register_connection() -> None:
    
    # JSON 파일에서 connection 정보 읽기
    with open('connections.json', 'r') as f:
        connections_data = json.load(f)

    # Airflow DB Session 시작
    session = Session()

    # 각 connection 정보를 Airflow에 등록
    for conn_id, conn_details in connections_data.items():
        # 해당 conn_id의 커넥션이 이미 존재하는지 확인
        existing_conn = session.query(Connection).filter(
            Connection.conn_id == conn_id
            ).first()
        
        # 커넥션이 존재하지 않는 경우에만 새로운 커넥션을 추가
        if not existing_conn:
            new_conn = Connection(
                conn_id=conn_id,
                conn_type=conn_details.get("conn_type", None),
                host=conn_details.get("host", None),
                login=conn_details.get("login", None),
                password=conn_details.get("password", None),
                port=conn_details.get("port", None),
                schema=conn_details.get("schema", None),
                extra=conn_details.get("extra", None),
                description=conn_details.get("description", None)   # Added description; using .get() to provide a default value in case it's not present
            )
            session.add(new_conn)
            logging.info(f"Added new connection: {conn_id}")

    # Commit and close the session
    session.commit()
    session.close()
    
if __name__ == "__main__":
    register_connection()
    print("All connections have been set!")