import tkinter as tk
from tkinter import messagebox
import json
import os

def calculate_manual_correction():
    try:
        duration = float(duration_entry.get())
        original_size = float(original_size_entry.get())
        compressed_size = float(compressed_size_entry.get())

        # Calcular el factor de corrección
        estimated_size = original_size  # Usamos el tamaño original como estimación inicial
        new_factor = compressed_size / estimated_size

        # Actualizar el factor de corrección
        update_correction_factor(new_factor)

        messagebox.showinfo("Éxito", f"Factor de corrección actualizado: {new_factor:.4f}")
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos.")

def update_correction_factor(new_factor):
    try:
        with open('correction_factor.json', 'r') as f:
            correction_data = json.load(f)
        current_factor = correction_data['factor']
        n = correction_data['n']
    except FileNotFoundError:
        current_factor = 1.0
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
root.title("Corrección Manual del Factor de Compresión")

# Sección para la corrección manual
tk.Label(root, text="Corrección Manual", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(root, text="Duración del video (segundos):").grid(row=1, column=0, sticky="w")
duration_entry = tk.Entry(root)
duration_entry.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Tamaño original (MB):").grid(row=2, column=0, sticky="w")
original_size_entry = tk.Entry(root)
original_size_entry.grid(row=2, column=1, sticky="w")

tk.Label(root, text="Tamaño comprimido (MB):").grid(row=3, column=0, sticky="w")
compressed_size_entry = tk.Entry(root)
compressed_size_entry.grid(row=3, column=1, sticky="w")

tk.Button(root, text="Calcular y Actualizar Factor de Corrección", command=calculate_manual_correction).grid(row=4, column=0, columnspan=2, pady=10)

correction_factor_label = tk.Label(root, text="Factor de corrección actual: N/A")
correction_factor_label.grid(row=5, column=0, columnspan=2)

# Cargar el factor de corrección actual si existe
if os.path.exists('correction_factor.json'):
    with open('correction_factor.json', 'r') as f:
        correction_data = json.load(f)
    current_factor = correction_data['factor']
    correction_factor_label.config(text=f"Factor de corrección actual: {current_factor:.4f}")

# Iniciar el bucle principal de tkinter
root.mainloop()
