@echo off
echo ==========================================
echo Launchly Physics Hub - Initializing...
echo ==========================================
echo.
echo Checking dependencies...
pip install -r requirements.txt

echo.
echo Launching Hub...
start /b python launchly_hub.py
exit
