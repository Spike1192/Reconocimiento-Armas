@echo off
echo ========================================
echo   SISTEMA DE DETECCION DE ARMAS
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo Error: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar si las dependencias están instaladas
echo Verificando dependencias...
python -c "import ultralytics, cv2, PyQt5" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Ejecutar el sistema
echo.
echo Iniciando sistema de deteccion de armas...
echo.
python Vista\weapon_detection_app.py

REM Si hay error, mostrar mensaje
if errorlevel 1 (
    echo.
    echo Error al ejecutar el sistema
    echo Verifica que todas las dependencias esten instaladas
    pause
)

REM Desactivar entorno virtual
call venv\Scripts\deactivate.bat 