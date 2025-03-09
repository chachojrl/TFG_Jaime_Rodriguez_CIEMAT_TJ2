@echo off

echo Instalando dependencias...

echo Dependencias instaladas correctamente.

echo Direccion en la que estoy
cd

echo Iniciando FastAPI con uvicorn en el directorio /src...
start cmd /k ".\venv\Scripts\activate && cd src && uvicorn csvllama2:app --reload"

echo Iniciando Streamlit en una nueva terminal en el directorio /src...
start cmd /k ".\venv\Scripts\activate && cd src && streamlit run main.py"

echo Procesos iniciados correctamente.
exit
