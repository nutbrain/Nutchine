@echo off
echo ====================================
echo Building Nutchine executable...
echo ====================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo.

REM Run PyInstaller
echo Running PyInstaller...
pyinstaller --clean build.spec

echo.
echo ====================================
echo Build completed!
echo ====================================
echo.
echo Executable location: dist\Nutchine.exe
echo.

if exist "dist\Nutchine.exe" (
    echo Build successful!
    echo.
    echo You can copy dist\Nutchine.exe to any location and run it directly.
    echo The config folder will be created automatically on first run.
) else (
    echo Build failed! Please check the errors above.
)

pause
