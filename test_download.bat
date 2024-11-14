@echo off
set "loader_type=fabric"
set "mc_version=1.21"
set "wd=%cd%\minecraft\wd"
set "md=%cd%\minecraft\md"
set "venvpy=%cd%\.venv\Scripts\python.exe"
"%venvpy%" -m pip install --no-input requests >NUL 2>NUL
"%venvpy%" main.py %loader_type% %mc_version%
"%venvpy%" -m pip uninstall -y requests >NUL 2>NUL
pause