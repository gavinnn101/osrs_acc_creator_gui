del /f "Gavins Account Creator.exe"
rmdir /s /q ..\src\dist
rmdir /s/ q ..\src\build
pyinstaller --key=PenguinMaster73! --name "Gavins Account Creator" --onefile ui_logic.py
copy ..\src\dist\"Gavins Account Creator.exe" ..\src\"Gavins Account Creator.exe"