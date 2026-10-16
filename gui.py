import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import json
from datetime import datetime
import pygame
import downloader

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Descargador(ctk.CTk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()
        self.reproduciendo = False

        self.title("Descargador de Música MP3 Pro")
        self.geometry("720x760")
        self.resizable(False, False)

        self.carpeta_destino = os.path.join(os.getcwd(), "Descargas")
        self.canciones_encontradas = []
        self.checkboxes = []

        # 1. Título y Switch de Modo Oscuro/Claro
        self.frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_titulo.pack(pady=(15, 10), padx=20, fill="x")

        self.lbl_titulo = ctk.CTkLabel(self.frame_titulo, text="Descargador de Música MP3 Pro", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(side="left")

        self.switch_tema = ctk.CTkSwitch(self.frame_titulo, text="Modo Oscuro", command=self.cambiar_tema)
        self.switch_tema.pack(side="right")
        self.switch_tema.select()

        # 2. Marco URL
        self.frame_url = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_url.pack(pady=5, padx=20, fill="x")

        self.entry_url = ctk.CTkEntry(self.frame_url, placeholder_text="Ingrese URL de YouTube o Spotify...", width=500)
        self.entry_url.pack(side="left", padx=(0, 10))

        self.btn_analizar = ctk.CTkButton(self.frame_url, text="Buscar", width=120, command=self.iniciar_analisis)
        self.btn_analizar.pack(side="left")

        # 3. Carpeta y Calidad de Audio
        self.frame_carpeta = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_carpeta.pack(pady=5, padx=20, fill="x")

        self.btn_carpeta = ctk.CTkButton(self.frame_carpeta, text="Seleccionar Carpeta", command=self.seleccionar_carpeta, width=150)
        self.btn_carpeta.pack(side="left", padx=(0, 10))

        self.lbl_carpeta = ctk.CTkLabel(self.frame_carpeta, text=self.carpeta_destino, text_color="gray", anchor="w")
        self.lbl_carpeta.pack(side="left", fill="x", expand=True)

        self.lbl_calidad = ctk.CTkLabel(self.frame_carpeta, text="Calidad:", font=("Arial", 12))
        self.lbl_calidad.pack(side="left", padx=(10, 5))

        self.opt_calidad = ctk.CTkOptionMenu(self.frame_carpeta, values=["128 kbps", "192 kbps", "320 kbps"], width=100)
        self.opt_calidad.set("192 kbps")
        self.opt_calidad.pack(side="right")

        # 4. Acciones y Reproductor
        self.frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acciones.pack(pady=(10, 5), padx=20, fill="x")

        self.btn_marcar_todas = ctk.CTkButton(self.frame_acciones, text="Marcar Todas", width=110, fg_color="#333333", command=self.marcar_todas)
        self.btn_marcar_todas.pack(side="left", padx=(0, 5))

        self.btn_desmarcar_todas = ctk.CTkButton(self.frame_acciones, text="Desmarcar Todas", width=110, fg_color="#333333", command=self.desmarcar_todas)
        self.btn_desmarcar_todas.pack(side="left", padx=(0, 10))

        self.btn_stop_preview = ctk.CTkButton(
            self.frame_acciones, text="⏹️ Detener Previa", width=120, 
            fg_color="#A91B0D", hover_color="#7C1309", command=self.detener_audio
        )
        self.btn_stop_preview.pack(side="left")

        self.lbl_contador = ctk.CTkLabel(self.frame_acciones, text="Canciones: 0", text_color="gray")
        self.lbl_contador.pack(side="right")

        # 5. Lista previsualización
        self.scroll_canciones = ctk.CTkScrollableFrame(self, width=660, height=180, label_text="Previsualización de Canciones")
        self.scroll_canciones.pack(pady=5, padx=20)

        # 6. Barras de Progreso
        self.frame_progreso = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_progreso.pack(pady=5, padx=20, fill="x")

        self.lbl_progreso_individual = ctk.CTkLabel(self.frame_progreso, text="Progreso canción: 0%", text_color="gray")
        self.lbl_progreso_individual.pack(anchor="w")
        
        self.bar_individual = ctk.CTkProgressBar(self.frame_progreso, width=660)
        self.bar_individual.pack(pady=(0, 8))
        self.bar_individual.set(0)

        self.lbl_progreso_general = ctk.CTkLabel(self.frame_progreso, text="Progreso general: 0/0", text_color="gray")
        self.lbl_progreso_general.pack(anchor="w")

        self.bar_general = ctk.CTkProgressBar(self.frame_progreso, width=660, progress_color="#1DB954")
        self.bar_general.pack(pady=(0, 5))
        self.bar_general.set(0)

        # 7. Botón Descargar
        self.btn_descargar = ctk.CTkButton(
            self, text="Descargar Seleccionadas", command=self.iniciar_descarga_seleccionadas, 
            fg_color="#1DB954", hover_color="#1aa34a", font=("Arial", 14, "bold"), height=38
        )
        self.btn_descargar.pack(pady=10)

        # 8. Logs y Botón Exportar Reporte
        self.frame_logs_header = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_logs_header.pack(pady=(5, 0), padx=20, fill="x")

        self.lbl_logs = ctk.CTkLabel(self.frame_logs_header, text="Registro de Actividad (Logs):", text_color="gray")
        self.lbl_logs.pack(side="left")

        self.btn_exportar = ctk.CTkButton(
            self.frame_logs_header, text="💾 Exportar Reporte", width=120, height=24,
            fg_color="#333333", hover_color="#222222", command=self.exportar_reporte
        )
        self.btn_exportar.pack(side="right")

        self.txt_logs = ctk.CTkTextbox(self, width=660, height=80)
        self.txt_logs.pack(pady=(5, 15))
        self.escribir_log("Pega un enlace de Spotify o YouTube y haz clic en 'Buscar'.")

    # --- MÉTODOS DE EXPORTACIÓN Y TEMAS ---

    def exportar_reporte(self):
        if not self.canciones_encontradas:
            messagebox.showwarning("Atención", "No hay un historial o lista de canciones para exportar.")
            return

        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de Texto (*.txt)", "*.txt"), ("Archivo JSON (*.json)", "*.json")],
            title="Guardar Reporte de Descarga"
        )

        if not ruta_archivo:
            return

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        contenido_log = self.txt_logs.get("1.0", "end").strip()

        try:
            if ruta_archivo.endswith(".json"):
                datos_json = {
                    "fecha": fecha_actual,
                    "carpeta_destino": self.carpeta_destino,
                    "calidad": self.opt_calidad.get(),
                    "total_canciones": len(self.canciones_encontradas),
                    "canciones": self.canciones_encontradas,
                    "registro_actividad": contenido_log.split("\n")
                }
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    json.dump(datos_json, f, ensure_ascii=False, indent=4)
            else:
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write("=== REPORTE DE DESCARGA - MUSIC DOWNLOADER PRO ===\n")
                    f.write(f"Fecha: {fecha_actual}\n")
                    f.write(f"Carpeta Destino: {self.carpeta_destino}\n")
                    f.write(f"Calidad seleccionada: {self.opt_calidad.get()}\n")
                    f.write(f"Total canciones en lista: {len(self.canciones_encontradas)}\n")
                    f.write("-" * 50 + "\n\n")
                    f.write("--- LISTA DE CANCIONES ---\n")
                    for idx, c in enumerate(self.canciones_encontradas, 1):
                        f.write(f"{idx}. {c['titulo']} - {c['artista']} (Álbum: {c.get('album', 'N/A')})\n")
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("--- REGISTRO DE ACTIVIDAD ---\n")
                    f.write(contenido_log + "\n")

            self.escribir_log(f"Reporte exportado con éxito en: {os.path.basename(ruta_archivo)}")
            messagebox.showinfo("Exportación Exitosa", "El reporte ha sido guardado correctamente.")

        except Exception as e:
            self.escribir_log(f"Error al guardar el reporte: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def cambiar_tema(self):
        if self.switch_tema.get() == 1:
            ctk.set_appearance_mode("dark")
            self.switch_tema.configure(text="Modo Oscuro")
            self.escribir_log("Apariencia cambiada a Modo Oscuro.")
        else:
            ctk.set_appearance_mode("light")
            self.switch_tema.configure(text="Modo Claro")
            self.escribir_log("Apariencia cambiada a Modo Claro.")

    # --- REPRODUCCIÓN EN STREAMING ---

    def reproducir_previa(self, busqueda):
        self.detener_audio()
        self.escribir_log(f"Cargando previsualización de: {busqueda}...")

        def _hilo_streaming():
            try:
                stream_url = downloader.obtener_stream_audio_youtube(busqueda)
                if stream_url:
                    pygame.mixer.music.load(stream_url)
                    pygame.mixer.music.play()
                    self.reproduciendo = True
                    self.escribir_log(f"▶️ Reproduciendo muestra de: {busqueda}")
                else:
                    self.escribir_log("No se pudo obtener la previsualización del audio.")
            except Exception as e:
                self.escribir_log(f"Error al reproducir vista previa: {e}")

        threading.Thread(target=_hilo_streaming, daemon=True).start()

    def detener_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.reproduciendo = False
            self.escribir_log("⏹️ Previsualización detenida.")

    # --- OPERACIONES GENERALES DE LA APP ---

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.carpeta_destino = ruta
            self.lbl_carpeta.configure(text=self.carpeta_destino)
            self.escribir_log(f"Carpeta actualizada: {self.carpeta_destino}")

    def escribir_log(self, texto):
        self.txt_logs.insert("end", f"> {texto}\n")
        self.txt_logs.see("end")

    def marcar_todas(self):
        for cb, _, _ in self.checkboxes:
            cb.select()

    def desmarcar_todas(self):
        for cb, _, _ in self.checkboxes:
            cb.deselect()

    def actualizar_progreso_individual(self, porcentaje, texto):
        self.bar_individual.set(porcentaje)
        self.lbl_progreso_individual.configure(text=f"Progreso canción: {int(porcentaje * 100)}% - {texto}")

    def iniciar_analisis(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Atención", "Ingresa una URL válida.")
            return

        self.detener_audio()
        self.btn_analizar.configure(state="disabled")
        self.escribir_log("Analizando enlace...")

        for widget in self.scroll_canciones.winfo_children():
            widget.destroy()
        self.checkboxes.clear()

        hilo = threading.Thread(target=self.proceso_analisis, args=(url,), daemon=True)
        hilo.start()

    def proceso_analisis(self, url):
        try:
            if "spotify.com" in url:
                self.canciones_encontradas = downloader.obtener_Spotify(url)
            elif "youtube.com" in url or "youtu.be" in url:
                self.canciones_encontradas = downloader.obtener_detalles_cancion(url)
            else:
                messagebox.showerror("Error", "URL no soportada. Usa Spotify o YouTube.")
                return

            for item in self.canciones_encontradas:
                row_frame = ctk.CTkFrame(self.scroll_canciones, fg_color="transparent")
                row_frame.pack(fill="x", pady=2, padx=5)

                texto_item = f"{item['titulo']} - {item['artista']}"
                var_check = ctk.CTkCheckBox(row_frame, text=texto_item)
                var_check.pack(side="left", anchor="w", expand=True)
                var_check.select()

                btn_play = ctk.CTkButton(
                    row_frame, text="🔊 Muestra", width=75, height=24, 
                    fg_color="#2B2B2B", hover_color="#1F1F1F",
                    command=lambda b=item['busqueda']: self.reproducir_previa(b)
                )
                btn_play.pack(side="right", padx=5)

                self.checkboxes.append((var_check, item, btn_play))

            self.lbl_contador.configure(text=f"Canciones: {len(self.canciones_encontradas)}")
            self.escribir_log(f"Se encontraron {len(self.canciones_encontradas)} canciones.")

        except Exception as e:
            self.escribir_log(f"Error durante el análisis: {e}")
            messagebox.showerror("Error de Análisis", str(e))
        finally:
            self.btn_analizar.configure(state="normal")

    def iniciar_descarga_seleccionadas(self):
        self.detener_audio()
        seleccionadas = [info for cb, info, _ in self.checkboxes if cb.get() == 1]

        if not seleccionadas:
            messagebox.showwarning("Atención", "No has seleccionado ninguna canción para descargar.")
            return

        self.btn_descargar.configure(state="disabled")
        self.btn_analizar.configure(state="disabled")

        hilo = threading.Thread(target=self.proceso_descarga, args=(seleccionadas,), daemon=True)
        hilo.start()

    def proceso_descarga(self, lista_a_descargar):
        total = len(lista_a_descargar)
        descargadas = 0
        omitidas = 0
        calidad_seleccionada = self.opt_calidad.get()

        self.escribir_log(f"Iniciando descarga de {total} canción(es) a {calidad_seleccionada}...")

        for idx, cancion in enumerate(lista_a_descargar, 1):
            try:
                self.lbl_progreso_general.configure(text=f"Progreso general: {idx}/{total}")
                self.bar_general.set(idx / total)

                self.escribir_log(f"[{idx}/{total}] Procesando: {cancion['titulo']} - {cancion['artista']}")
                
                resultado = downloader.descargar_y_etiquetar_cancion(
                    cancion, 
                    self.carpeta_destino, 
                    calidad=calidad_seleccionada,
                    callback_progreso=self.actualizar_progreso_individual
                )

                if resultado == "OMITIDO":
                    omitidas += 1
                    self.escribir_log("--> Archivo omitido (ya existe en la carpeta).")
                else:
                    descargadas += 1

            except Exception as e:
                self.escribir_log(f"Error descargando {cancion['titulo']}: {e}")

        self.bar_individual.set(1.0)
        self.lbl_progreso_individual.configure(text="Progreso canción: 100% - Completado")
        
        resumen_msg = f"Proceso finalizado ({calidad_seleccionada}).\n\nDescargadas: {descargadas}\nOmitidas (duplicadas): {omitidas}"
        self.escribir_log(f"¡Completado! Nuevas: {descargadas} | Omitidas: {omitidas}")
        messagebox.showinfo("Resumen de Descarga", resumen_msg)

        self.btn_descargar.configure(state="normal")
        self.btn_analizar.configure(state="normal")


if __name__ == "__main__":
    app = Descargador()
    app.mainloop()