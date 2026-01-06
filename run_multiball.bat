@echo off

:: Change to the project directory.
cd /d "%~dp0"

:: Set Python path
set PYTHONPATH=%cd%

:: Default to dbpop if no specific flag is provided
set target_module=src.multiball.dbpop

:: Parse command line arguments to find module flags
:parse_args
if "%1"=="" goto end_parse
if "%1"=="--db" (
    set target_module=src.multiball.dbpop
    shift
    goto parse_args
)
if "%1"=="--dl" (
    set target_module=src.multiball.downloader
    shift
    goto parse_args
)
if "%1"=="--pl" (
    set target_module=src.multiball.plotter
    shift
    goto parse_args
)
if "%1"=="--sk" (
    set target_module=src.multiball.skeeter
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [--db^|--dl^|--pl^|--sk] [module_arguments]
    echo.
    echo Flags:
    echo   --db    Run database population module (default)
    echo   --dl    Run downloader module
    echo   --pl    Run plotter module
    echo   --sk    Run skeeter module
    echo.
    echo If no flag is provided, --db (dbpop) is used by default.
    echo All other arguments are passed to the selected module.
    exit /b 0
)
if "%1"=="-h" (
    echo Usage: %0 [--db^|--dl^|--pl^|--sk] [module_arguments]
    echo.
    echo Flags:
    echo   --db    Run database population module (default)
    echo   --dl    Run downloader module
    echo   --pl    Run plotter module
    echo   --sk    Run skeeter module
    echo.
    echo If no flag is provided, --db (dbpop) is used by default.
    echo All other arguments are passed to the selected module.
    exit /b 0
)
shift
goto parse_args

:end_parse

:: Run the selected module with remaining arguments
echo Running: python -m %target_module% %*
python -m %target_module% %*