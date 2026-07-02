@echo off
setlocal enableextensions
title Avvio NetPulse

:: Lavora sempre dalla cartella dove si trova questo .bat
cd /d "%~dp0"

echo ==============================================
echo       NetPulse - Super Scanner Launcher
echo ==============================================
echo.

:: 1. Trova un comando Python valido (python o py -3)
set "PY_CMD="
python --version >nul 2>&1
if %errorlevel%==0 set "PY_CMD=python"

if not defined PY_CMD (
    py -3 --version >nul 2>&1
    if %errorlevel%==0 set "PY_CMD=py -3"
)

if not defined PY_CMD (
    echo [ERRORE CRITICO] Python non e' installato o non e' presente nel PATH.
    echo Scarica Python da https://www.python.org/downloads/
    echo Durante l'installazione abilita "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [OK] Interprete Python rilevato: %PY_CMD%

:: 2. Verifica pip
%PY_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] pip non disponibile in questo ambiente Python.
    echo Prova a reinstallare Python includendo pip.
    echo.
    pause
    exit /b 1
)

echo [OK] Controllo/installazione dipendenze Python...
echo (Potrebbe richiedere qualche secondo al primo avvio)
%PY_CMD% -m pip install --disable-pip-version-check --quiet customtkinter fpdf scapy
if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Installazione dipendenze non riuscita.
    echo Verifica connessione Internet e permessi di installazione pacchetti.
    pause
    exit /b 1
)

:: 3. Nmap non e' obbligatorio per avviare la GUI, ma serve per la scansione server.
nmap --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVVISO] Nmap non trovato nel PATH.
    echo La funzione "Analisi Sicurezza (Nmap)" potrebbe non funzionare.
    echo Scarica Nmap da: https://nmap.org/download.html
    echo.
)

echo [OK] Avvio NetPulse...
echo.

:: 4. Avvio applicazione
%PY_CMD% "%~dp0netpulse.py"
set "APP_EXIT=%errorlevel%"

if %APP_EXIT% neq 0 (
    echo.
    echo [ATTENZIONE] NetPulse si e' chiuso con errore (codice %APP_EXIT%).
    echo Controlla il messaggio sopra per i dettagli.
    pause
    exit /b %APP_EXIT%
)

exit /b 0
