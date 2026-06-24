@echo off
chcp 65001 >nul
title MHR Mod Tool - Build EXE

echo ============================================
echo   MHR Mod Tool - Build EXE
echo ============================================
echo.

REM Direct path to Python
set "PYTHON_EXE=D:\python.exe"

echo [1/4] Checking Python...
if not exist "%PYTHON_EXE%" (
    echo Error: Python not found at %PYTHON_EXE%
    pause
    exit /b 1
)

%PYTHON_EXE% --version
echo.

echo [2/4] Cleaning old files...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "MHR_Armor_Bone_Renamer.spec" del "MHR_Armor_Bone_Renamer.spec"
if exist "MHR_Mod_Tool_v1.2.spec" del "MHR_Mod_Tool_v1.2.spec"
if exist "MHR_Mod_Tool_v1.3.spec" del "MHR_Mod_Tool_v1.3.spec"
echo   Done
echo.

echo [3/4] Installing dependencies...
%PYTHON_EXE% -m pip install --upgrade pyinstaller py7zr rarfile tkinterdnd2 openpyxl pybcj
echo.

echo [4/4] Building EXE (this may take 1-3 minutes)...
%PYTHON_EXE% -m PyInstaller --onefile --windowed --name "MHR_Mod_Tool_v1.3" --hidden-import=py7zr --hidden-import=py7zr.cli --hidden-import=rarfile --hidden-import=tkinterdnd2 --hidden-import=openpyxl --hidden-import=pybcj --collect-all=py7zr --collect-all=rarfile --collect-all=tkinterdnd2 --collect-all=pybcj --clean --noconfirm MHR_Armor_Bone_Renamer.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo   BUILD FAILED!
    echo ============================================
    pause
    exit /b 1
)

echo.
echo ============================================
echo   BUILD SUCCESS!
echo ============================================
echo.
echo Output: %~dp0dist\MHR_Mod_Tool_v1.3.exe
echo.
pause
