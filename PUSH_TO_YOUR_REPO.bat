@echo off
echo.
echo ========================================
echo   Push to GitHub Repository
echo   https://github.com/ankit1141r/ride_by_my_idea.git
echo ========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing git repository...
    git init
    echo.
)

REM Check current remote
echo Checking git remote...
git remote -v
echo.

REM Remove old origin if exists and add new one
git remote remove origin 2>nul
echo Adding remote origin...
git remote add origin https://github.com/ankit1141r/ride_by_my_idea.git
echo.

REM Set branch to main
echo Setting branch to main...
git branch -M main
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
git commit -m "feat: Complete ride-hailing platform with Railway deployment support - Backend API, Web Frontend, Android Apps"
echo.

REM Push to GitHub
echo.
echo ========================================
echo   PUSHING TO GITHUB
echo ========================================
echo.
echo Repository: https://github.com/ankit1141r/ride_by_my_idea.git
echo.
pause

git push -u origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo Your repository: https://github.com/ankit1141r/ride_by_my_idea
    echo.
    echo ========================================
    echo   NEXT: Deploy to Railway.app
    echo ========================================
    echo.
    echo 1. Go to https://railway.app
    echo 2. Sign in with GitHub
    echo 3. Click "New Project"
    echo 4. Select "Deploy from GitHub repo"
    echo 5. Choose: ankit1141r/ride_by_my_idea
    echo 6. Add PostgreSQL database
    echo 7. Add Redis database
    echo 8. Configure environment variables
    echo.
    echo See RAILWAY_QUICK_START.md for details
    echo.
) else (
    echo.
    echo ========================================
    echo   PUSH FAILED
    echo ========================================
    echo.
    echo This might be due to:
    echo 1. Authentication required - use GitHub Personal Access Token
    echo 2. Repository doesn't exist - create it first at:
    echo    https://github.com/new
    echo.
    echo Try running these commands manually:
    echo   git remote add origin https://github.com/ankit1141r/ride_by_my_idea.git
    echo   git branch -M main
    echo   git push -u origin main
    echo.
)

echo.
pause
