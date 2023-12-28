pyinstaller --noconfirm --onefile "%cd%\darlene.pyw"
del "darlene.spec"
rmdir /s /q build
move %cd%\dist\darlene.exe %cd%
rmdir /s /q dist