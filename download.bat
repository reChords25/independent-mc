@echo off
set "loader_type=fabric"
set "mc_version=1.21"
set "install_mods=true"

set "wd=%cd%\minecraft\wd"
set "md=%cd%\minecraft\md"

python --version >NUL
if ERRORLEVEL 1 GOTO NOPYTHON
goto :HASPYTHON

:NOPYTHON
echo [ERROR] Python is not installed or on PATH
echo [INFO] Install Python or consider adding the Path of python.exe to PATH
echo [INFO] Press any key to exit...
pause >NUL
goto :eof

:HASPYTHON
echo [INFO] Python installation found
echo [INFO] Creating python virtual environment
python -m venv "%cd%\.venv"
set "venvpy=%cd%\.venv\Scripts\python.exe"

echo [INFO] Installing portablemc via pip
"%venvpy%" -m pip install --no-input portablemc[certifi] >NUL 2>NUL

echo [INFO] Installing Minecraft %loader_type%, version %mc_version% into "%wd%"
echo[
"%venvpy%" -m portablemc --main-dir "%md%" --work-dir "%wd%" --output human start %loader_type%:%mc_version% --dry
echo[

if "%install_mods%%" == "true" (
    echo [INFO] Installing additional content
    echo[
    "%venvpy%" -m pip install --no-input requests >NUL 2>NUL
    "%venvpy%" additional-content-downloader\main.py %loader_type% %mc_version%
    "%venvpy%" -m pip uninstall -y requests >NUL 2>NUL
    echo[
) else if "%install_mods%%" == "false" (
    echo [INFO] Skipping additional content installation
    echo[
)

echo [INFO] Creating start.bat file
(
   echo set "wd=%cd%\minecraft\wd"
   echo set "md=%cd%\minecraft\md"
   echo start .venv\Scripts\python.exe -m portablemc --main-dir "%md%" --work-dir "%wd%" --output human-color start %loader_type%:%mc_version%
) > start.bat

echo [INFO] Everything done
echo [INFO] Press any key to exit...
pause >NUL
goto :eof

