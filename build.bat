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
set yyyy=%date:~0,4%
set mm=%date:~5,2%
set dd=%date:~8,2%
set build_number=%yyyy%%mm%%dd%
echo flutter build windows --release --build-number %build_number% --build-name=%version%
call flutter build windows --release --build-number %build_number% --build-name=%version%

mkdir dist\copybook
xcopy /e /Y .\build\windows\runner\Release .\dist\copybook\
%~dp0\tools\7z a %~dp0\dist\copybook_%version%_windows_x64.7z %~dp0\dist\copybook
scp -P 6302 %~dp0\dist\copybook_%version%_windows_x64.7z allan@home.mydata.top:/mnt/zhanmei/nas/allan/ÎÒµÄÈí¼þ/copybook/