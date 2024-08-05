import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import shlex
import json
import psutil
import signal

def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, file_path)
    if file_path:
        calculate_output_size()

def show_help(file_name):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'src', 'messages', file_name)
        with open(file_path, 'r') as file:
            content = file.read()
        help_window = tk.Toplevel(root)
        help_window.title("Ayuda")
        text_widget = tk.Text(help_window, wrap=tk.WORD)
        text_widget.insert(tk.END, content)
        text_widget.pack(expand=True, fill=tk.BOTH)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se pudo encontrar el archivo de ayuda: {file_name}")

def calculate_output_size():
    input_file = input_file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Por favor, selecciona un archivo de entrada.")
        return

    scale = scale_var.get()
    bitrate_video = int(bitrate_video_var.get())
    framerate = int(framerate_var.get())
    audio_channels = int(audio_channels_var.get())
    bitrate_audio = int(bitrate_audio_var.get())
    sample_rate = int(sample_rate_var.get().split()[0])

    # Calcular duración del video
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
    duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())

    # Calcular tamaño estimado
    video_size = (bitrate_video * 1000 * duration) / 8
    audio_size = (bitrate_audio * 1000 * duration) / 8
    total_size = (video_size + audio_size) / (1024 * 1024)  # Convertir a MB

    # Cargar el factor de corrección
    try:
        with open('correction_factor.json', 'r') as f:
            correction_data = json.load(f)
        correction_factor = correction_data['factor']
    except FileNotFoundError:
        correction_factor = 1.08  # Valor por defecto si no existe el archivo

    estimated_size = total_size * correction_factor

    size_label.config(text=f"Tamaño estimado: {estimated_size:.2f} MB")

def run_ffmpeg():
    global ffmpeg_process
    input_file = input_file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Por favor, selecciona un archivo de entrada.")
        return

    output_file = os.path.splitext(input_file)[0] + "_compressed.mp4"
    scale = scale_var.get().split()[0]  # Eliminar "Horizontal" o "Vertical"
    bitrate_video = bitrate_video_var.get()
    framerate = framerate_var.get()
    audio_channels = audio_channels_var.get()
    bitrate_audio = bitrate_audio_var.get()
    sample_rate = sample_rate_var.get().split()[0]

    command = f'ffmpeg -i "{input_file}" -vf {scale} -b:v {bitrate_video}k -r {framerate} -ac {audio_channels} -b:a {bitrate_audio}k -ar {sample_rate} "{output_file}"'

    ffmpeg_process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, preexec_fn=os.setsid)

    update_ffmpeg_output()

def update_ffmpeg_output():
    if ffmpeg_process.poll() is None:
        try:
            output = ffmpeg_process.stdout.readline()
            if output:
                ffmpeg_output.insert(tk.END, output)
                ffmpeg_output.see(tk.END)
            root.after(100, update_ffmpeg_output)
        except (ValueError, AttributeError):
            pass
    else:
        messagebox.showinfo("Éxito", "Video comprimido guardado.")
        update_correction_factor()

def stop_ffmpeg():
    if ffmpeg_process:
        parent = psutil.Process(ffmpeg_process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        messagebox.showinfo("Detenido", "El proceso de conversión ha sido detenido.")

def update_correction_factor():
    input_file = input_file_entry.get()
    output_file = os.path.splitext(input_file)[0] + "_compressed.mp4"

    # Obtener el tamaño real del archivo comprimido
    real_size = os.path.getsize(output_file) / (1024 * 1024)  # Tamaño en MB

    # Obtener el tamaño estimado
    estimated_size = float(size_label.cget("text").split(":")[1].strip().split()[0])

    # Calcular el nuevo factor de corrección
    new_factor = real_size / estimated_size

    # Cargar el factor de corrección actual
    try:
        with open('correction_factor.json', 'r') as f:
            correction_data = json.load(f)
        current_factor = correction_data['factor']
        n = correction_data['n']
    except FileNotFoundError:
        current_factor = 1.08
        n = 0

    # Actualizar el factor de corrección
    updated_factor = (current_factor * n + new_factor) / (n + 1)
    n += 1

    # Guardar el nuevo factor de corrección
    with open('correction_factor.json', 'w') as f:
        json.dump({'factor': updated_factor, 'n': n}, f)

    correction_factor_label.config(text=f"Factor de corrección actual: {updated_factor:.4f}")

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
scale_var = tk.StringVar(value='scale=512:288 Horizontal')
tk.OptionMenu(root, scale_var, 'scale=512:288 Horizontal', 'scale=288:512 Vertical').grid(row=1, column=1, sticky="w")

tk.Label(root, text="Bitrate de video (k):").grid(row=2, column=0, sticky="w")
bitrate_video_var = tk.StringVar(value="120")
bitrate_video_menu = ttk.Combobox(root, textvariable=bitrate_video_var, values=[200, 180, 170, 165, 160, 155, 150, 145, 140, 135, 130, 125, 120, 115, 110, 105, 100, 95, 90, 85, 80, 75, 70, 65])
bitrate_video_menu.grid(row=2, column=1, sticky="w")
tk.Button(root, text="?", command=lambda: show_help("01_Bitrate_de_video.md")).grid(row=2, column=2)

tk.Label(root, text="Framerate:").grid(row=3, column=0, sticky="w")
framerate_var = tk.StringVar(value="15")
framerate_menu = ttk.Combobox(root, textvariable=framerate_var, values=[15, 24, 30])
framerate_menu.grid(row=3, column=1, sticky="w")
tk.Button(root, text="?", command=lambda: show_help("02-Framerate.md")).grid(row=3, column=2)

tk.Label(root, text="Canales de audio:").grid(row=4, column=0, sticky="w")
audio_channels_var = tk.StringVar(value="1")
audio_channels_menu = ttk.Combobox(root, textvariable=audio_channels_var, values=[1, 2])
audio_channels_menu.grid(row=4, column=1, sticky="w")
tk.Button(root, text="?", command=lambda: show_help("03-Canales-de-audio.md")).grid(row=4, column=2)

tk.Label(root, text="Bitrate de audio (k):").grid(row=5, column=0, sticky="w")
bitrate_audio_var = tk.StringVar(value="27")
bitrate_audio_menu = ttk.Combobox(root, textvariable=bitrate_audio_var, values=[320, 192, 160, 144, 128, 112, 96, 80, 64, 56, 48, 40, 32, 30, 27, 26, 24, 20, 19, 18, 16])
bitrate_audio_menu.grid(row=5, column=1, sticky="w")
tk.Button(root, text="?", command=lambda: show_help("04-Bitrate-de-audio.md")).grid(row=5, column=2)

tk.Label(root, text="Sample rate:").grid(row=6, column=0, sticky="w")
sample_rate_var = tk.StringVar(value="44100 Hz")
sample_rate_menu = ttk.Combobox(root, textvariable=sample_rate_var, values=["96000 Hz", "48000 Hz", "44100 Hz", "32000 Hz", "24000 Hz", "22050 Hz", "16000 Hz"])
sample_rate_menu.grid(row=6, column=1, sticky="w")
tk.Button(root, text="?", command=lambda: show_help("05-Sample-rate.md")).grid(row=6, column=2)

# Botones
tk.Button(root, text="Calcular tamaño", command=calculate_output_size).grid(row=7, column=0, columnspan=3, pady=10)
size_label = tk.Label(root, text="Tamaño estimado: N/A")
size_label.grid(row=8, column=0, columnspan=3)

tk.Button(root, text="Comprimir video", command=run_ffmpeg).grid(row=9, column=0, columnspan=2, pady=10)
tk.Button(root, text="Stop", command=stop_ffmpeg).grid(row=9, column=2, pady=10)

# Factor de corrección
correction_factor_label = tk.Label(root, text="Factor de corrección actual: N/A")
correction_factor_label.grid(row=10, column=0, columnspan=3)

# Salida de ffmpeg
ffmpeg_output = tk.Text(root, wrap=tk.WORD, width=70, height=10, bg="black", fg="white")
ffmpeg_output.grid(row=11, column=0, columnspan=3, pady=10)

# Iniciar el bucle principal de tkinter
root.mainloop()
