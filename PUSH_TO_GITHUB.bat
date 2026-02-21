@echo off
echo.
echo ========================================
echo   Push RideConnect to GitHub
echo ========================================
echo.

REM Check git status
echo Checking git status...
git status
echo.

REM Add all files
echo Adding all files...
git add .
echo.

REM Show what will be committed
echo Files staged for commit:
git status --short
echo.

REM Commit
echo Committing changes...
git commit -m "feat: Add Railway deployment configuration and complete ride-hailing platform"
echo.

REM Check remote
echo Checking git remote...
git remote -v
echo.

REM Push
echo.
echo ========================================
echo   PUSHING TO GITHUB
echo ========================================
echo.
echo If this is your first push, you may need to:
echo   1. Create a repository on GitHub
echo   2. Run: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo   3. Run: git branch -M main
echo   4. Run: git push -u origin main
echo.
pause

git push

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo NEXT STEPS:
    echo   1. Go to https://railway.app
    echo   2. Sign in with GitHub
    echo   3. Click 'New Project'
    echo   4. Select 'Deploy from GitHub repo'
    echo   5. Choose your repository
    echo   6. Add PostgreSQL and Redis databases
    echo   7. Configure environment variables
    echo.
    echo See RAILWAY_QUICK_START.md for details
) else (
    echo.
    echo ========================================
    echo   PUSH FAILED - Manual Setup Required
    echo ========================================
    echo.
    echo Run these commands manually:
    echo.
    echo 1. Create a new repository on GitHub
    echo    Go to: https://github.com/new
    echo.
    echo 2. Set up remote and push:
    echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
    echo    git branch -M main
    echo    git push -u origin main
    echo.
    echo 3. Then deploy to Railway
    echo    See RAILWAY_QUICK_START.md
)

echo.
pause
