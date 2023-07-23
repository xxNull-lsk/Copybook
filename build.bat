flutter build windows --release

mkdir dist\copybook
xcopy /e .\build\windows\runner\Release .\dist\copybook\