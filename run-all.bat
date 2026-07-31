@echo off
REM Bam dup file nay la chay ca backend lan giao dien.
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python run-all.py
if errorlevel 1 pause
