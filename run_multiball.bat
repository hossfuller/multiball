@echo off

:: Change to the project directory.
cd /d "%~dp0"

:: Set Python path
set PYTHONPATH=%cd%

:: Default to dbpop if no specific flag is provided
set target_module=src.multiball.dbpop

:: Initialize arguments for the target module
set module_args=

:: Parse command line arguments to find module flags
:parse_args
if "%1"=="" goto end_parse

:: Check for module flags
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

:: If it's not a recognized module flag, add it to the arguments for the module
set module_args=%module_args% %1
shift
goto parse_args

:end_parse

:: Run the selected module with the collected arguments
python -m %target_module% %module_args%