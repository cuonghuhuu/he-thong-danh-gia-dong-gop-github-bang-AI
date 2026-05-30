@echo off
setlocal

cd /d "%~dp0"
set PYGAME_HIDE_SUPPORT_PROMPT=1

echo [1/4] Cai dat thu vien can thiet...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Loi: Khong cai duoc requirements.
    exit /b 1
)

echo [2/4] Xoa ban build cu...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "GitHub Contribution AI.spec" del /q "GitHub Contribution AI.spec"

echo [3/4] Dong goi ung dung bang PyInstaller...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name "GitHub Contribution AI" ^
  --add-data "main_window.ui;." ^
  --hidden-import "matplotlib.backends.backend_qtagg" ^
  app.py

if errorlevel 1 (
    echo Loi: Build exe that bai.
    exit /b 1
)

echo [4/4] Hoan tat.
echo File exe nam tai: dist\GitHub Contribution AI\GitHub Contribution AI.exe
echo Khi gui cho nguoi khac, hay gui ca thu muc: dist\GitHub Contribution AI

endlocal
