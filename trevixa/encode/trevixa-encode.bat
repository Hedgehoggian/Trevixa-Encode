@echo off
setlocal
set ROOT_DIR=%~dp0
set VENV_DIR=%ROOT_DIR%\.venv

if not exist "%VENV_DIR%" (
  py -3.14 -m venv "%VENV_DIR%" 2>nul || py -3 -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

if "%1"=="--gui" (
  if exist "%ROOT_DIR%\build\trevixa-encode.exe" (
    "%ROOT_DIR%\build\trevixa-encode.exe" --gui
    exit /b %ERRORLEVEL%
  ) else (
    echo C++ GUI binary not built yet. Build with CMake first.
    exit /b 1
  )
)

python "%ROOT_DIR%\python\main.py" --cli --interactive
