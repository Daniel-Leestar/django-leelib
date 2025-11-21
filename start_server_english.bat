@echo off
chcp 936
REM

set VENV_DIR=venv
set ACTIVATE_SCRIPT=%VENV_DIR%\Scripts\activate.bat
set REQUIREMENTS=requirements.txt

REM --- Function: Check, Create, and Activate Virtual Environment ---
:SETUP_VENV
    echo ------------------------------------------
    echo Checking for virtual environment...

    if exist %ACTIVATE_SCRIPT% (
        echo Virtual environment '%VENV_DIR%' already exists.
        goto ACTIVATE
    )

    echo Virtual environment '%VENV_DIR%' not found. Creating it now...
    py -m venv %VENV_DIR%

    if not exist %ACTIVATE_SCRIPT% (
        echo.
        echo Error: Failed to create virtual environment. Please ensure the 'py' command is available.
        goto END
    )

    :ACTIVATE
    echo Activating virtual environment...
    call %ACTIVATE_SCRIPT%

    echo ------------------------------------------
    echo Checking and installing project dependencies...
    if exist %REQUIREMENTS% (
        pip install -r %REQUIREMENTS%
        if errorlevel 1 (
            echo.
            echo Error: Failed to install dependencies. Please check the contents of %REQUIREMENTS%.
            goto END
        )
        echo Dependencies installed successfully.
    ) else (
        echo Warning: %REQUIREMENTS% file not found. Skipping dependency installation.
        echo Please ensure required dependencies - including Django - are installed manually.
    )

    goto RUN_SERVER

REM --- Start Server ---
:RUN_SERVER
    echo ------------------------------------------
    echo Starting Django server [py manage.py runserver 0.0.0.0:8000]...
    echo Server will listen on all addresses at port 8000

    REM Core command: Use 'py' to run manage.py runserver, listening on all IPs
    py manage.py runserver 0.0.0.0:8000

    goto END

REM --- End Script ---
:END
    echo ------------------------------------------
    echo Server stopped or failed to run.
    pause