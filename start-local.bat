@echo off
chcp 65001 > nul
echo JH 견적시스템 로컬 실행
echo ========================
echo 백엔드: http://localhost:8000
echo 프론트엔드: http://localhost:3000
echo API 문서: http://localhost:8000/docs
echo.
echo [Ctrl+C 로 종료]
echo.

:: 백엔드를 새 창으로 실행
start "JH-Estimate Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"

:: 잠시 대기 후 프론트엔드 실행
timeout /t 2 /nobreak > nul
start "JH-Estimate Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo 두 서버가 새 창으로 실행됩니다.
pause
