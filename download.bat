@echo off
:: Set loader (vanilla, fabric, forge, neoforge, legacyfabric, quilt)
set "loader_type=fabric"
:: Set Minecraft Version
set "mc_version=1.21"
:: Whether to install mods, resourcepacks etc.
set "install_content=false"
:: Email address to use for authentication (Microsoft account)
:: Only really  necessary for multiplayer! Leave emtpy if not needed
set "auth_mail="

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

if "%install_content%" == "true" (
    echo [INFO] Installing additional content
    echo[
    "%venvpy%" -m pip install --no-input requests >NUL 2>NUL
    "%venvpy%" additional-content-downloader\main.py %loader_type% %mc_version%
    "%venvpy%" -m pip uninstall -y requests >NUL 2>NUL
    echo[
) else if "%install_content%" == "false" (
    echo [INFO] Skipping additional content installation
    echo[
)

if "%loader_type%" == "vanilla" (
    set "loader_type="
) else (
    set "loader_type=%loader_type%:"
)

echo [INFO] Creating start.bat file
(
   if "%auth_mail%" == "" (
       echo start .venv\Scripts\python.exe -m portablemc --main-dir "%md%" --work-dir "%wd%" --output human-color start %loader_type%%mc_version%
   ) else (
       echo start .venv\Scripts\python.exe -m portablemc --main-dir "%md%" --work-dir "%wd%" --output human-color start --login %auth_mail% %loader_type%%mc_version%
   )
) > start.bat

echo [INFO] Everything done
echo [INFO] Press any key to exit...
pause >NUL
goto :eof

