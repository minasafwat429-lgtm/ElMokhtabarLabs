@echo off
echo Starting ElMokhtabar Backend Server...
echo =======================================
echo.

REM Try using 'python' command
python backend/run.py
if %ERRORLEVEL% EQU 0 goto end

echo.
echo 'python' command not found or failed. Trying 'py'...
REM Try using 'py' command (Python Launcher)
py backend/run.py
if %ERRORLEVEL% EQU 0 goto end

echo.
echo 'py' command also failed. Technical details:
echo Please ensure Python is installed and added to your PATH.
echo.
pause
goto :eof

:end
echo.
echo Server stopped.
pause
