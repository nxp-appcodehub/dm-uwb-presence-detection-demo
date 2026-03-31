@echo off

REM
REM Copyright 2025 NXP
REM
REM NXP Proprietary. This software is owned or controlled by NXP and may only be
REM used strictly in accordance with the applicable license terms. By expressly
REM accepting such terms or by downloading, installing, activating and/or otherwise
REM using the software, you are agreeing that you have read, and that you agree to
REM comply with and are bound by, such license terms. If you do not agree to be
REM bound by the applicable license terms, then you may not retain, install,
REM activate or otherwise use the software.
REM

setlocal

echo Searching for FRDM-RW612 running Plug and Play application

for /f "delims=" %%C in ('python detect_com.py') do (
    set "COM_PORT=%%C"
)

if not defined COM_PORT (
    echo No FRDM-RW612 found
    pause
    exit /b 1
)

echo FRDM-RW612 found %COM_PORT%

python demo_presence_detection.py %COM_PORT% max_distance=500

pause
exit /b 0