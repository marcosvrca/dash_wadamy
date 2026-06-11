@echo off
setlocal EnableExtensions

cd /d "%~dp0"
title Wadamy - Dashboard

echo ============================================
echo   Wadamy - Inventario de Maquinas
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    echo Instale o Python 3 em https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" na instalacao.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

echo Instalando dependencias...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo --------------------------------------------
echo Dashboard local:  http://localhost:5000
echo API dos agentes:  http://localhost:5000/api/inventario
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        echo IP desta maquina: %%b
        echo URL para os agentes: http://%%b:5000/api/inventario
    )
)

echo --------------------------------------------
echo Mantenha esta janela aberta enquanto usa o dashboard.
echo Para encerrar, feche a janela ou pressione Ctrl+C.
echo.

python dashboard\app.py

echo.
echo Dashboard encerrado.
pause
