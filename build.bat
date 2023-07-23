
set version=1.0.7
set build_number=1011
flutter build windows --release -v --build-number %build_number% --build-name=%version%

mkdir dist\copybook
xcopy /e /Y .\build\windows\runner\Release .\dist\copybook\