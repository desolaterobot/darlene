pyinstaller --noconfirm --onefile --windowed "%cd%\darlene.py"
del "darlene.spec"
rmdir /s /q build
move %cd%\dist\darlene.exe %cd%
rmdir /s /q dist