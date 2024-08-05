import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shlex

def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)

def calculate_output_size():
    input_file = input_file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Por favor, selecciona un archivo de entrada.")
        return

    scale = scale_var.get()
    bitrate_video = int(bitrate_video_entry.get())
    framerate = int(framerate_entry.get())
    audio_channels = int(audio_channels_entry.get())
    bitrate_audio = int(bitrate_audio_entry.get())
    sample_rate = int(sample_rate_entry.get())

    # Calcular duración del video
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
    duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())

    # Calcular tamaño estimado
    video_size = (bitrate_video * 1000 * duration) / 8
    audio_size = (bitrate_audio * 1000 * duration) / 8
    total_size = (video_size + audio_size) / (1024 * 1024)  # Convertir a MB

    # Añadir un factor de corrección basado en la compresión
    correction_factor = 1.08  # Ajusta este valor según sea necesario
    estimated_size = total_size * correction_factor

    size_label.config(text=f"Tamaño estimado: {estimated_size:.2f} MB")

def run_ffmpeg():
    input_file = input_file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Por favor, selecciona un archivo de entrada.")
        return

    output_file = os.path.splitext(input_file)[0] + "_compressed.mp4"
    scale = scale_var.get()
    bitrate_video = bitrate_video_entry.get()
    framerate = framerate_entry.get()
    audio_channels = audio_channels_entry.get()
    bitrate_audio = bitrate_audio_entry.get()
    sample_rate = sample_rate_entry.get()

    command = f'ffmpeg -i "{input_file}" -vf {scale} -b:v {bitrate_video}k -r {framerate} -ac {audio_channels} -b:a {bitrate_audio}k -ar {sample_rate} "{output_file}"'

    try:
        subprocess.run(shlex.split(command), check=True)
        messagebox.showinfo("Éxito", f"Video comprimido guardado como: {output_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Ha ocurrido un error al comprimir el video.")

# Crear ventana principal
root = tk.Tk()
root.title("Compresor de Video FFmpeg")

# Archivo de entrada
tk.Label(root, text="Archivo de entrada:").grid(row=0, column=0, sticky="w")
input_file_entry = tk.Entry(root, width=50)
input_file_entry.grid(row=0, column=1)
tk.Button(root, text="Seleccionar", command=select_input_file).grid(row=0, column=2)

# Parámetros
tk.Label(root, text="Escala:").grid(row=1, column=0, sticky="w")
scale_var = tk.StringVar(value='scale=512:288')
tk.OptionMenu(root, scale_var, 'scale=512:288', 'scale=288:512').grid(row=1, column=1, sticky="w")

tk.Label(root, text="Bitrate de video (k):").grid(row=2, column=0, sticky="w")
bitrate_video_entry = tk.Entry(root)
bitrate_video_entry.insert(0, "120")
bitrate_video_entry.grid(row=2, column=1, sticky="w")

tk.Label(root, text="Framerate:").grid(row=3, column=0, sticky="w")
framerate_entry = tk.Entry(root)
framerate_entry.insert(0, "15")
framerate_entry.grid(row=3, column=1, sticky="w")

tk.Label(root, text="Canales de audio:").grid(row=4, column=0, sticky="w")
audio_channels_entry = tk.Entry(root)
audio_channels_entry.insert(0, "1")
audio_channels_entry.grid(row=4, column=1, sticky="w")

tk.Label(root, text="Bitrate de audio (k):").grid(row=5, column=0, sticky="w")
bitrate_audio_entry = tk.Entry(root)
bitrate_audio_entry.insert(0, "27")
bitrate_audio_entry.grid(row=5, column=1, sticky="w")

tk.Label(root, text="Sample rate:").grid(row=6, column=0, sticky="w")
sample_rate_entry = tk.Entry(root)
sample_rate_entry.insert(0, "44100")
sample_rate_entry.grid(row=6, column=1, sticky="w")

# Botones
tk.Button(root, text="Calcular tamaño", command=calculate_output_size).grid(row=7, column=0, columnspan=3, pady=10)
size_label = tk.Label(root, text="Tamaño estimado: N/A")
size_label.grid(row=8, column=0, columnspan=3)

tk.Button(root, text="Comprimir video", command=run_ffmpeg).grid(row=9, column=0, columnspan=3, pady=10)

# Iniciar el bucle principal de tkinter
root.mainloop()
