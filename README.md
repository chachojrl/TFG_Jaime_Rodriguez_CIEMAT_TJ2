# Proyecto de Análisis de Espectrogramas TJ-II

## Descripción
Este proyecto proporciona una aplicación basada en inteligencia artificial para analizar y responder preguntas de los experimentos del TJ-II. Incluye funcionalidades para cargar datos, generar consultas SQL, visualizar gráficos, y predecir desórdenes MHD utilizando un modelo de aprendizaje automático.

## Estructura del Proyecto

```
/
|-- data/
|   |-- processed/
|   |-- raw/
|
|-- docs/
|-- scripts/
|-- src/
|   |-- config/
|   |-- spectograms/
|   |   |-- spectograms_for_ai_learning/
|   |   |-- spectograms_for_try/
|
|-- utilities/
|   |-- raw_data/
|
|-- venv/
|-- .env
|-- .gitignore
|-- README.md
|-- requirements.txt
```

## Instalación
1. Clonar el repositorio y moverse al directorio del proyecto:
   ```bash
   git clone https://github.com/chachojrl/TFG_Jaime_Rodriguez_CIEMAT_TJ2.git
   cd TFG_Jaime_Rodriguez_CIEMAT_TJ2
   ```

2. Crear y activar un entorno virtual con Python 3.12:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # En macOS/Linux
   venv\Scripts\activate     # En Windows
   ```

3. Instalar dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## Instalación de Ollama y Llama 3
Si se desea utilizar **Ollama con Llama 3**, es necesario instalar Ollama y descargar el modelo correspondiente:
```bash
curl -fsSL https://ollama.com/install.sh | sh  # Para macOS y Linux
```
En **Windows**, descargar y ejecutar el instalador desde: [https://ollama.com/download](https://ollama.com/download)

Una vez instalado, descargar el modelo **Llama 3** ejecutando:
```bash
ollama pull llama3
```

## Uso

### Configurar SSL antes de ejecutar la aplicación
En **Windows** (PowerShell):
```powershell
$env:SSL_CERT_FILE = (python -c "import certifi; print(certifi.where())")
```

En **macOS/Linux (bash/zsh):**
```bash
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
```

### Ejecutar la Aplicación Principal
```bash
cd src
python main.py
```
Esto iniciará la interfaz Gradio donde se pueden realizar consultas sobre los espectrogramas.

### Funcionalidades de la Interfaz Gradio
A través del chat en Gradio, se pueden realizar las siguientes acciones:
- **Predecir MHD:** Analizando si un espectrograma presenta desórdenes MHD.
- **Consultar datos del CSV:** Extraer información relevante en base a consultas en lenguaje natural.
- **Dibujar gráficos de señales:** Visualizar datos en forma de gráficos a partir de señales específicas.
- **Generar respuesta general:** Respondiendo preguntas a cuestiones generales.

## Configuración de Modelos de Lenguaje (LLM)
El sistema permite utilizar dos modelos de lenguaje diferentes:
- **Ollama (Llama 3)**: Implementado en `ai_parser.py`.
- **IBM Watson (meta-llama/llama-3-3-70b-instruct)**: Implementado en `ai_parser_2.py`.

Para cambiar el modelo utilizado, se debe modificar la importación en `src/main.py`, cambiando:
```python
from ai_parser import ...
```
a:
```python
from ai_parser_2 import ...
```
Esto permitirá utilizar el modelo alternativo según la necesidad del usuario.

### Instalación de Ollama y Llama 3
Si se desea utilizar **Ollama con Llama 3**, es necesario instalar Ollama y descargar el modelo correspondiente:
```bash
curl -fsSL https://ollama.com/install.sh | sh  # Para macOS y Linux
```
En **Windows**, descargar y ejecutar el instalador desde: [https://ollama.com/download](https://ollama.com/download)

Una vez instalado, descargar el modelo **Llama 3** ejecutando:
```bash
ollama pull llama3
```
Sistema permite utilizar dos modelos de lenguaje diferentes:
- **Ollama (Llama 3)**: Implementado en `ai_parser.py`.
- **IBM Watson (meta-llama/llama-3-3-70b-instruct)**: Implementado en `ai_parser_2.py`.

Para cambiar el modelo utilizado, se debe modificar la importación en `src/main.py`, cambiando:
```python
from ai_parser import ...
```
a:
```python
from ai_parser_2 import ...
```
Esto permitirá utilizar el modelo alternativo según la necesidad del usuario.

## Datos Binarios
Los nuevos datos binarios deben almacenarse en la carpeta `utilities/raw_data/` con el siguiente formato:
```plaintext
MIR5C_(numero de descarga)_(numero de descarga).txt
```
Ejemplo:
```plaintext
MIR5C_12345_12345.txt
```

## Dependencias
- Python 3.12
- [requirements.txt](./requirements.txt)

## Configuración
El archivo `src/config_loader.py` carga configuraciones desde archivos de texto y modelos dentro de `./config/`.

