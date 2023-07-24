@echo off

cd /d %~dp0
del /s /q /f %~dp0\dist\copybook
rd /s /q %~dp0\dist\copybook

set /p major_version=<%~dp0.major_version
set /p minor_version=<%~dp0.minor_version
set /p fixed_version=<%~dp0.fixed_version
if "%major_version%"=="" set major_version=1
if "%minor_version%"=="" set minor_version=0
if "%fixed_version%"=="" set fixed_version=0

set version=%major_version%.%minor_version%.%fixed_version%
set yyyy=%date:~3,4%
set mm=%date:~8,2%
set dd=%date:~11,2%
set build_number=%yyyy%%mm%%dd%
call flutter build windows --release -v --build-number %build_number% --build-name=%version%

mkdir dist\copybook
xcopy /e /Y .\build\windows\runner\Release .\dist\copybook\
%~dp0\tools\7z a %~dp0\dist\copybook_%version%_windows_x64.7z %~dp0\dist\copybook