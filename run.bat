@echo off
chcp 65001 > nul
echo ========================================================
echo   2026년 화신그룹 정규직 전환 입사확인 시스템 실행기
echo ========================================================
echo.
echo [1] 서버를 구동 중입니다... (http://localhost:8000)
echo [2] 관리자 대시보드 주소: http://localhost:8000/admin
echo [3] 종료하려면 Ctrl + C 를 누르세요.
echo.
python app.py
pause
