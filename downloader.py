import os
import requests
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, ID3NoHeaderError

def incrustar_portada(ruta_mp3, titulo, artista, album="", url_portada=""):
    try:
        try:
            audio = ID3(ruta_mp3)
        except ID3NoHeaderError:
            audio = ID3()

        if titulo:
            audio.add(TIT2(encoding=3, text=titulo))
        if artista:
            audio.add(TPE1(encoding=3, text=artista))
        if album:
            audio.add(TALB(encoding=3, text=album))

        if url_portada:
            try:
                respuesta = requests.get(url_portada, timeout=10)
                if respuesta.status_code == 200:
                    audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=respuesta.content))
            except Exception as img_err:
                print(f"Error al descargar la portada: {img_err}")

        audio.save(ruta_mp3)
        print(f"Metadatos incrustados correctamente en: {os.path.basename(ruta_mp3)}")
    except Exception as e:
        print(f"Error al incrustar metadatos en {ruta_mp3}: {e}")

def obtener_Spotify(url_spotify):
    load_dotenv(override=True)

    CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")  

    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlist_id = url_spotify.split("/")[-1].split("?")[0]
    resultados = sp.playlist_items(playlist_id)
    lista_canciones = []

    for item in resultados['items']:
        pista = item.get('track')
        if pista and pista.get('name'):
            nombre = pista['name']
            artista = pista['artists'][0]['name'] if pista.get('artists') else "Desconocido"
            album = pista['album']['name'] if pista.get('album') else ""
            
            url_portada = ""
            if pista.get('album') and pista['album'].get('images'):
                url_portada = pista['album']['images'][0]['url']

            lista_canciones.append({
                'busqueda': f"{nombre} {artista}",
                'titulo': nombre,
                'artista': artista,
                'album': album,
                'portada': url_portada
            })

    return lista_canciones

def obtener_detalles_cancion(url):
    """
    Extrae la lista de títulos/videos de una playlist o video de YouTube sin descargar el audio.
    """
    opciones = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True
    }

    lista_canciones = []
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                if entry:
                    lista_canciones.append({
                        'busqueda': entry.get('title', 'Desconocido'),
                        'titulo': entry.get('title', 'Desconocido'),
                        'artista': entry.get('uploader', 'Desconocido'),
                        'album': 'YouTube Playlist',
                        'portada': ''
                    })
        else:
            lista_canciones.append({
                'busqueda': info.get('title', 'Desconocido'),
                'titulo': info.get('title', 'Desconocido'),
                'artista': info.get('uploader', 'Desconocido'),
                'album': 'YouTube',
                'portada': info.get('thumbnail', '')
            })
    return lista_canciones

def progreso(d):
    if d['status'] == 'downloading':
        porcentaje = d.get('_percent_str', '0.0%')
        velocidad = d.get('_speed_str', '0.0 B/s')
        tiempo_restante = d.get('_eta_str', 'N/A')
        print(f"Descargando: {porcentaje} a {velocidad}, tiempo restante: {tiempo_restante}", end='\r')
    elif d['status'] == 'finished':
        print("\nDescarga completada. Procesando audio...")

def descargar_y_etiquetar_cancion(info_cancion, carpeta_destino, calidad="192", callback_progreso=None):
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    busqueda = info_cancion['busqueda']
    
    titulo_limpio = info_cancion['titulo'].replace('/', '-').replace('\\', '-')
    artista_limpio = info_cancion['artista'].replace('/', '-').replace('\\', '-')
    
    nombre_archivo = f"{titulo_limpio} - {artista_limpio}.mp3"
    ruta_salida = os.path.join(carpeta_destino, nombre_archivo)

    # Detección de duplicados
    if os.path.exists(ruta_salida):
        print(f"El archivo ya existe. Omitiendo descarga: {nombre_archivo}")
        if callback_progreso:
            callback_progreso(1.0, "Omitido (Ya existe)")
        return "OMITIDO"

    def hook_progreso(d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                porcentaje = float(p_str) / 100.0
                if callback_progreso:
                    callback_progreso(porcentaje, f"Descargando: {d.get('_percent_str', '0%')}")
            except ValueError:
                pass
        elif d['status'] == 'finished':
            if callback_progreso:
                callback_progreso(1.0, "Convirtiendo a MP3...")

    quality_val = str(calidad).split()[0]

    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(carpeta_destino, f"{titulo_limpio} - {artista_limpio}.%(ext)s"),
        'postprocessors': [{    
            'key': 'FFmpegExtractAudio',    
            'preferredcodec': 'mp3',
            'preferredquality': quality_val,
        }],
        'ignoreerrors': True,
        'default_search': 'ytsearch1',
        'quiet': True,
        'progress_hooks': [hook_progreso]
    }

    print(f"Buscando, descargando y etiquetando ({quality_val} kbps): {busqueda}")
    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([f"ytsearch1:{busqueda}"])

    if os.path.exists(ruta_salida):
        incrustar_portada(
            ruta_mp3=ruta_salida, 
            titulo=info_cancion['titulo'], 
            artista=info_cancion['artista'], 
            album=info_cancion.get('album', ''), 
            url_portada=info_cancion.get('portada', '')
        )
    return "DESCARGADO"

def procesar_playlist_spotify(url_spotify, carpeta_destino):
    print(f"Obteniendo canciones de la playlist de Spotify: {url_spotify}")
    canciones = obtener_Spotify(url_spotify)
    print(f"Se encontraron {len(canciones)} canciones. Iniciando descargas...")
    
    for i, cancion in enumerate(canciones, 1):
        print(f"\n[{i}/{len(canciones)}] Procesando: {cancion['titulo']} - {cancion['artista']}")
        descargar_y_etiquetar_cancion(cancion, carpeta_destino)

    print(f"\n¡Todas las canciones de la playlist se han descargado en: {carpeta_destino}!")


def descargar_audio_youtube(url, carpeta_destino):
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(carpeta_destino, '%(title)s.%(ext)s'),
        'postprocessors': [{    
            'key': 'FFmpegExtractAudio',    
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ignoreerrors': True,
        'progress_hooks': [progreso],
    }
    print(f"Descargando audio de: {url}")

    with yt_dlp.YoutubeDL(opciones) as ydl:
        ydl.download([url])

    print(f"Descarga completada. Los archivos se han guardado en: {carpeta_destino}")

def obtener_stream_audio_youtube(busqueda):
    """
    Busca en YouTube y retorna la URL directa del stream de audio para reproducirlo en streaming.
    """
    opciones = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'ytsearch1',
        'skip_download': True
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(f"ytsearch1:{busqueda}", download=False)
        if 'entries' in info and info['entries']:
            return info['entries'][0].get('url')
        elif 'url' in info:
            return info.get('url')
    return None

if __name__ == "__main__":
    url = input("Introduce la URL del video de YouTube o Playlist: ")
    carpeta_destino = input("Introduce la carpeta de destino: ")
    descargar_audio_youtube(url, carpeta_destino)