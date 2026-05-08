@echo off
REM ============================================================
REM  Data Seekers – Panam NoSQL Project
REM  setup.bat — Instalación del entorno (Windows)
REM
REM  USO: Doble clic en setup.bat, o ejecuta en CMD:
REM       setup.bat
REM ============================================================

setlocal enabledelayedexpansion
title Data Seekers - Setup de Entorno

echo.
echo  =====================================================
echo   Data Seekers ^– Panam NoSQL Project
echo   Setup de Entorno ^(Windows^)
echo  =====================================================
echo.

REM ── 1. Verificar Python ──────────────────────────────────
echo [1/6] Verificando Python 3.10+...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  X Python no encontrado.
    echo    Descargalo en: https://www.python.org/downloads/
    echo    Asegurate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  OK Python %PYVER% encontrado

REM ── 2. Crear entorno virtual ─────────────────────────────
echo.
echo [2/6] Creando entorno virtual (.venv)...

if exist ".venv" (
    echo  Aviso: .venv ya existe. Omitiendo creacion.
    echo         Borra la carpeta .venv para recrearlo limpio.
) else (
    python -m venv .venv
    echo  OK Entorno virtual creado en .venv\
)

REM ── 3. Activar entorno virtual ────────────────────────────
echo.
echo [3/6] Activando entorno virtual...
call .venv\Scripts\activate.bat
echo  OK Entorno activado

REM ── 4. Instalar dependencias ──────────────────────────────
echo.
echo [4/6] Instalando dependencias desde requirements.txt...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo  X Error instalando dependencias.
    pause
    exit /b 1
)
echo  OK Dependencias instaladas

REM ── 5. Crear .env ─────────────────────────────────────────
echo.
echo [5/6] Configurando variables de entorno...

if exist ".env" (
    echo  Aviso: .env ya existe. No se sobreescribira.
) else (
    copy .env.example .env >nul
    echo  OK .env creado desde .env.example
    echo     Edita .env si necesitas cambiar host/puertos de BD
)

REM ── 6. Verificar Docker ───────────────────────────────────
echo.
echo [6/6] Verificando Docker...

docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  OK Docker disponible
    echo.
    echo     Para levantar MongoDB y Cassandra:
    echo     docker-compose up -d mongodb cassandra
) else (
    echo  Aviso: Docker no encontrado.
    echo         Descargalo en: https://www.docker.com/products/docker-desktop/
)

REM ── Resumen ───────────────────────────────────────────────
echo.
echo  =====================================================
echo   Setup completado exitosamente
echo  =====================================================
echo.
echo  Proximos pasos:
echo.
echo  1. El entorno virtual ya esta activo en esta ventana.
echo     Para activarlo en otra terminal:
echo     .venv\Scripts\activate
echo.
echo  2. Levanta las bases de datos:
echo     docker-compose up -d mongodb cassandra
echo.
echo  3. Espera ~30s y ejecuta los notebooks en orden:
echo     jupyter notebook
echo     00 -^> 01 -^> 02 -^> 03 -^> 04
echo.
pause
