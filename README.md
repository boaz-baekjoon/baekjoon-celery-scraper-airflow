# 🚀 개요
- 백준 코딩테스트를 준비하는 사람들을 위해 문제 추천용 봇 서비스를 제공하기 위해 데이터 파이프라인를 구축했습니다. 
- Airflow, FastApi, Celery(Worker), Redis, Postgresql를 사용하여 데이터 수집용 파이프라인을 구성. 
- 이를 통해 모델링과 시각화를 통해 백준 인사이트를 제공할 수 있습니다.

# 📌 사용 데이터 
| 데이터 출처 | 데이터 분류  | 데이터 설명                              | 
|--------|---------|-------------------------------------|
 | 백준, Solved.ac   | 유저 데이터  | 백준과 Solved.ac API을 공통으로 이용하는 유저 데이터 |
| 백준, Solved.ac | 문제 데이터  | 백준과 Solved.ac API를 통해 수집하는 문제와 문제의 메타데이터 |            
| 백준 | 문제집 데이터 | 백준에서 삼성기출문제처럼 문제집과 문제의 ID를 담고 있는 정보 | 

# 🔗 데이터 파이프라인

![data pipeline](https://www.notion.so/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F9c4d9e71-2131-4a4b-a258-69886d03a1a8%2Fe7f6d7d6-a18e-4554-af01-3cdd16a299df%2FUntitled.png?table=block&id=851f9564-ead6-495e-83f1-8891ad096f00&spaceId=9c4d9e71-2131-4a4b-a258-69886d03a1a8&width=1810&userId=62eab6d5-74a0-4d71-841e-0418b39ef555&cache=v2)

# 📚 DB ERD

### Raw-Data ERD

![rawdata_erd](https://www.notion.so/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F9c4d9e71-2131-4a4b-a258-69886d03a1a8%2Fe379e38f-1746-433a-8a07-f34f502c724d%2F%25E1%2584%2587%25E1%2585%25A2%25E1%2586%25A8%25E1%2584%258C%25E1%2585%25AE%25E1%2586%25AB_ERD.jpeg?table=block&id=ac2f9a36-ced4-4a6a-8dc1-1fe61ad77f7b&spaceId=9c4d9e71-2131-4a4b-a258-69886d03a1a8&width=1810&userId=62eab6d5-74a0-4d71-841e-0418b39ef555&cache=v2)
