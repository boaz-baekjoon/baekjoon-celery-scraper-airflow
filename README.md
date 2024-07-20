# 🚀 백준 코딩테스트 추천 봇 데이터 파이프라인

## 📊 프로젝트 개요

백준 코딩테스트를 준비하는 사람들을 위한 문제 추천 봇 서비스의 데이터 파이프라인 구축 프로젝트입니다.

### 🛠 사용 기술
- Airflow
- FastAPI
- Celery (Worker)
- Redis
- PostgreSQL

### 🎯 목표
모델링과 시각화를 통해 백준 인사이트를 제공하고, 개인화된 문제 추천 서비스 구현

## 🔗 프로젝트 상세 정보
[프로젝트 정리 링크](https://www.yuki-dev-blog.site/projects/baekjoon-data-pipeline-project)

## 📌 데이터 소스

| 출처 | 분류 | 설명 |
|------|------|------|
| 백준, Solved.ac | 유저 데이터 | 공통 API를 이용한 유저 정보 |
| 백준, Solved.ac | 문제 데이터 | 문제 및 메타데이터 |
| 백준 | 문제집 데이터 | 문제집과 문제 ID 정보 (예: 삼성 기출문제) |

## 🔄 데이터 파이프라인
![데이터 파이프라인 구조](https://i.postimg.cc/52FkbbLR/Untitled.png)

## 📚 데이터베이스 ERD
### Raw-Data ERD
![Raw 데이터 ERD](https://i.postimg.cc/1zGCVBW0/ERD.jpg)
