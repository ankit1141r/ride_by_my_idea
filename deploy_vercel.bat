@echo off
title Deploy RideConnect India to Vercel
echo =======================================================
echo 🚀 Deploying RideConnect India to Vercel
echo =======================================================
echo.
echo Checking for Vercel CLI...
echo.
call npx vercel --prod
echo.
echo =======================================================
echo If you have not logged in yet, run: npx vercel login
echo Then re-run this script to deploy directly to production!
echo =======================================================
pause
