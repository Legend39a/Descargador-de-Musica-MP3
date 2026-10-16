# Descargador de Música MP3

Aplicación de escritorio en Python con interfaz gráfica moderna para buscar canciones a partir de un enlace de **YouTube** o **Spotify**, previsualizarlas, elegir cuáles descargar y guardarlas como **MP3** con sus metadatos (título, artista, álbum y portada).

> Proyecto personal desarrollado en septiembre de 2026 con fines de aprendizaje.


## Funcionalidades

- Análisis de enlaces de YouTube (video o lista) y de listas de reproducción de Spotify.
- Lista de canciones con casillas para marcar o desmarcar todas o solo algunas.
- Previsualización de audio de cada canción antes de descargarla.
- Calidad de audio a elegir: 128, 192 o 320 kbps.
- Barras de progreso por canción y general, y registro de actividad en pantalla.
- Detección de canciones duplicadas, que se omiten.
- Etiquetado automático de los MP3 con título, artista, álbum y portada.
- Exportación del reporte de actividad en `.txt` o `.json`.
- Modo oscuro y modo claro.

## Tecnologías

Python · CustomTkinter · pygame · yt-dlp · Spotipy (API de Spotify) · Mutagen · python-dotenv · FFmpeg

## Estructura del proyecto

```
Descargador-de-Musica-MP3/
├── main.py            # Punto de entrada
├── gui.py             # Interfaz gráfica (CustomTkinter)
├── downloader.py      # Lógica de búsqueda, descarga y etiquetado
├── requirements.txt   # Dependencias de Python
├── .env.example       # Plantilla de credenciales de Spotify
├── .gitignore
├── LICENSE
└── README.md
```

## Requisitos previos

1. **Python 3.10 o superior.**
2. **FFmpeg** instalado y disponible en el PATH (necesario para convertir a MP3). En Windows:
   ```bash
   winget install Gyan.FFmpeg
   ```
   Cierra y vuelve a abrir la terminal, y comprueba con `ffmpeg -version`.
3. **Credenciales de Spotify** (solo para enlaces de Spotify):
   - Entra a [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) y crea una aplicación.
   - Copia el *Client ID* y el *Client Secret*.

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/Legend39a/Descargador-de-Musica-MP3.git
cd Descargador-de-Musica-MP3

# 2. Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\activate        # En Linux/macOS: source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar las credenciales
copy .env.example .env        # En Linux/macOS: cp .env.example .env
# Abre .env y escribe tu Client ID y tu Client Secret

# 5. Ejecutar
python main.py
```

## Cómo se usa

1. Pega un enlace de YouTube o de una lista de Spotify y pulsa **Buscar**.
2. Marca las canciones que quieres y, si lo deseas, escucha una muestra.
3. Elige la carpeta de destino y la calidad.
4. Pulsa **Descargar Seleccionadas** y sigue el progreso.

## Aviso legal

Este proyecto es educativo y de uso personal. Spotify se usa solo para obtener la información de las listas; el audio se busca en YouTube. Descarga únicamente contenido sobre el que tengas derechos o permiso, y respeta los derechos de autor y los términos de servicio de YouTube y Spotify.

## Autor

**Estiben Lopez Garcia** · Estudiante de Ingeniería en Software, Tecnológico de Antioquia
[GitHub](https://github.com/Legend39a) · [LinkedIn](https://www.linkedin.com/in/estiben-lopez-garcia-b44325257)
