#!/bin/bash

scrapyd &

# 배포 스크립트 실행
scrapyd-deploy --project=baekjoon_scraper

# 컨테이너가 계속 실행되도록 대기
wait
