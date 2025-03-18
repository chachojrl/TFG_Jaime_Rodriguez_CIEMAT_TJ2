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
python src/main.py
```
Esto iniciará la interfaz Gradio donde se pueden realizar consultas sobre los espectrogramas.

### Funcionalidades de la Interfaz Gradio
A través del chat en Gradio, se pueden realizar las siguientes acciones:
- **Predecir MHD:** Analizando si un espectrograma presenta desórdenes MHD.
- **Consultar datos del CSV:** Extraer información relevante en base a consultas en lenguaje natural.
- **Dibujar gráficos de señales:** Visualizar datos en forma de gráficos a partir de señales específicas.
- **Generar respuesta general:** Respondiendo preguntas a cuestiones generales.

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