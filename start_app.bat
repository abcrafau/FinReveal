@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Brak lokalnego srodowiska Python. Zainstaluj zaleznosci zgodnie z README.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8510 --server.address 127.0.0.1 --browser.gatherUsageStats false
