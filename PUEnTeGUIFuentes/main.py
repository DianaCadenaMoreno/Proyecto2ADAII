import tkinter as tk
from tkinter import filedialog, ttk
import os
import subprocess

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("PUEnTe GUI")

        # Crear estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Marco principal
        self.main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)  # La columna 0 (main_frame) se expandirá horizontalmente
        self.root.rowconfigure(0, weight=1)     # La fila 0 (main_frame) se expandirá verticalmente

        # Etiqueta para selección de archivo
        self.label_file = ttk.Label(self.main_frame, text="Selecciona un archivo de texto:")
        self.label_file.grid(row=0, column=0, columnspan=2, pady=10)

        # Botón para seleccionar archivo
        self.btn_browse = ttk.Button(self.main_frame, text="Subir archivo", command=self.browse_file)
        self.btn_browse.grid(row=1, column=0, pady=10, padx=5)

        # Botón para resolver
        self.btn_solve = ttk.Button(self.main_frame, text="Resolver", command=self.solve_mzn)
        self.btn_solve.grid(row=1, column=1, pady=10, padx=5)

        # Etiqueta para datos de entrada
        self.label_input = ttk.Label(self.main_frame, text="Datos de entrada:")
        self.label_input.grid(row=2, column=0, columnspan=2, pady=10)

        # Cuadro de texto para entrada
        self.textbox = tk.Text(self.main_frame, height=10, width=60)
        self.textbox.grid(row=3, column=0, columnspan=2, pady=10, sticky='nsew')  # Configuración adicional

        # Barra de desplazamiento vertical para el cuadro de texto
        scrollbar = ttk.Scrollbar(self.main_frame, command=self.textbox.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.textbox.config(yscrollcommand=scrollbar.set)

        # Etiqueta para resultados
        self.label_result = ttk.Label(self.main_frame, text="Resultados:")
        self.label_result.grid(row=4, column=0, columnspan=2, pady=10)

        # Cuadro de texto para resultados
        self.result_textbox = tk.Text(self.main_frame, height=10, width=60)
        self.result_textbox.grid(row=5, column=0, columnspan=2, pady=10, sticky='nsew')  # Configuración adicional

        # Barra de desplazamiento vertical para el cuadro de texto de resultados
        scrollbar_result = ttk.Scrollbar(self.main_frame, command=self.result_textbox.yview)
        scrollbar_result.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.result_textbox.config(yscrollcommand=scrollbar_result.set)

        # Configurar colores y fuentes
        for label in [self.label_file, self.label_input, self.label_result]:
            label.config(font=('Helvetica', 12, 'bold'), foreground='blue')

        self.btn_browse.config(style="TButton", padding=(5, 5))
        self.btn_solve.config(style="TButton", padding=(5, 5))
        self.textbox.config(font=('Courier', 10))
        self.result_textbox.config(font=('Courier', 10))

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if file_path:
            self.selected_file_name = os.path.splitext(os.path.basename(file_path))[0]  # Obtener el nombre del archivo sin extensión
            with open(file_path, "r") as file:
                content = file.read()
                self.textbox.delete(1.0, tk.END)
                self.textbox.insert(tk.END, content)

    def solve_mzn(self):
        try:
            # Obtener el contenido del cuadro de texto
            input_content = self.textbox.get("1.0", tk.END)

            # Convertir el contenido del archivo de texto al formato DZN
            lines = input_content.strip().split('\n')
            J = int(lines[0])
            K = int(lines[1])

            # Definir los nombres de los parámetros
            param_names = ["Ej", "Aj", "Gj", "Fj", "Vj", "Pj", "Pj_max", "Supj", "Infj", "P0j", "Dk", "Rk"]

            # Obtener las líneas con valores y convertirlas al formato DZN
            param_lines = []
            for i, line in enumerate(lines[2:]):
                values = line.split(', ')
                param_lines.append(f"{param_names[i]} = [ {', '.join(values)} ];")

            # Crear el contenido DZN
            dzn_content = f"J = {J};\nK = {K};\n"
            dzn_content += '\n'.join(param_lines)

            # Obtener el nombre del archivo seleccionado
            selected_file_name = getattr(self, "selected_file_name", "temp_input")
            
            # Guardar el contenido DZN en un archivo temporal en DatosPUEnTe
            data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'DatosPUEnTe')
            tmp_dzn_path = os.path.join(data_folder, f"{selected_file_name}.dzn")
            print(f"Guardando DZN en: {tmp_dzn_path}")
            print(f"Contenido DZN:\n{dzn_content}")
            try:
                with open(tmp_dzn_path, "w") as tmp_dzn_file:
                    tmp_dzn_file.write(dzn_content)
            except Exception as e:
                print(f"Error al guardar el archivo DZN: {e}")
                return

            #Encerrar la ruta del archivo DZN entre comillas para manejar espacios en la ruta
            tmp_dzn_path = f'"{tmp_dzn_path}"'

            # Ejecutar modelo PUEnTe.mzn con el archivo DZN usando HiGHS como solver
            minizinc_command = f'minizinc --solver coinbc --all-solutions PUEnTe.mzn {tmp_dzn_path}'
            print(f"Ejecutando: {minizinc_command}")
            result = subprocess.run(minizinc_command, shell=True, capture_output=True, text=True)

            # Mostrar el resultado en el cuadro de texto de resultados
            self.result_textbox.delete(1.0, tk.END)
            self.result_textbox.insert(tk.END, result.stdout)
            if result.stderr:
                self.result_textbox.insert(tk.END, f"\nError: {result.stderr}")

        except Exception as e:
            print(f"Error general durante la ejecución: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()






