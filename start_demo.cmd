@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Heart Talk AI Demo
set "NO_PROXY=127.0.0.1,localhost"
set "no_proxy=127.0.0.1,localhost"

set "LOG_FILE=%~dp0startup.log"
echo [%date% %time%] Launcher started.>"%LOG_FILE%"

if exist "server.pid" (
  set /p OLD_PID=<"server.pid"
  if defined OLD_PID taskkill /PID !OLD_PID! /F >nul 2>nul
  del /Q "server.pid" >nul 2>nul
  timeout /t 1 /nobreak >nul
)

set "PYTHON_EXE="
where python.exe >nul 2>nul
if not errorlevel 1 set "PYTHON_EXE=python.exe"
if not defined PYTHON_EXE if exist "D:\miniconda\python.exe" set "PYTHON_EXE=D:\miniconda\python.exe"
if not defined PYTHON_EXE if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python313\python.exe"

if not defined PYTHON_EXE (
  echo [ERROR] Python was not found.>>"%LOG_FILE%"
  echo.
  echo [ERROR] Python was not found.
  echo Install Python and enable Add Python to PATH.
  echo Log: %LOG_FILE%
  goto :hold
)

echo Python: %PYTHON_EXE%>>"%LOG_FILE%"

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo [ERROR] .env was missing and has been created.>>"%LOG_FILE%"
  echo.
  echo [SETUP] The .env file has been created.
  echo Put your DeepSeek key after AI_API_KEY= and save it.
  start "" notepad.exe ".env"
  goto :hold
)

set "AI_KEY="
for /f "usebackq tokens=1,* delims==" %%A in (".env") do if /I "%%A"=="AI_API_KEY" set "AI_KEY=%%B"
if not defined AI_KEY (
  echo [ERROR] AI_API_KEY is empty.>>"%LOG_FILE%"
  echo.
  echo [SETUP] DeepSeek API key is empty.
  echo Put your key after AI_API_KEY=, save, and run again.
  start "" notepad.exe ".env"
  goto :hold
)

echo Starting server...>>"%LOG_FILE%"
echo.
echo Heart Talk AI Demo is starting...
echo Open: http://127.0.0.1:8080
echo Keep this window open while using the demo.
echo.
"%PYTHON_EXE%" -u server.py 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo [%date% %time%] Server exited with code %EXIT_CODE%.>>"%LOG_FILE%"
echo.
echo [STOPPED] Server exit code: %EXIT_CODE%
echo See startup.log if there is an error.

:hold
echo.
pause
endlocal
