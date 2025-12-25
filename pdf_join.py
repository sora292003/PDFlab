import os, io, textwrap, math, threading, subprocess, re, sys, json
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# --- FIX PARA PYINSTALLER ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- TEMAS ---
THEMES = {
    "XP": {
        "bg": "#ECE9D8", "container": "#F5F5F0", "accent": "#0055E5", "btn": "#245EDB", 
        "btn_run": "#388E3C", "text": "#000000", "list_bg": "#FFFFFF", "border": "#7F9DB9",
        "font": "Tahoma", "radius": 0
    },
    "LUMINOUS": {
        "bg": "#F2F7FA", "container": "#E1EBF5", "accent": "#00B4D8", "btn": "#00B4D8", 
        "btn_run": "#00B4D8", "text": "#003366", "list_bg": "#F2F7FA", "border": "#00B4D8",
        "font": "Courier New", "radius": 0
    },
    "HACKER": {
        "bg": "#0A0A0A", "container": "#1A1A1A", "accent": "#00FF41", "btn": "#333333", 
        "btn_run": "#00FF41", "text": "#00FF41", "list_bg": "#000000", "border": "#00FF41",
        "font": "Consolas", "radius": 0
    },
    "DARK_PRO": { 
        "bg": "#2B2B2B", "container": "#363636", "accent": "#5294E2", "btn": "#404040", 
        "btn_run": "#5294E2", "text": "#E0E0E0", "list_bg": "#1E1E1E", "border": "#505050",
        "font": "Segoe UI", "radius": 5
    }
}

class PDFLogic:
    @staticmethod
    def crear_separador(titulo):
        packet = io.BytesIO()
        try:
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFillColor(colors.black)
            can.setFont("Courier-Bold", 18)
            lineas = textwrap.wrap(titulo, width=45)
            y_inicio = A4[1]/2 + ((len(lineas)/2)*25)
            for i, linea in enumerate(lineas):
                can.drawCentredString(A4[0]/2, y_inicio - (i*25), linea.upper())
            can.setLineWidth(0.5)
            can.line(150, y_inicio - (len(lineas)*25) - 10, A4[0]-150, y_inicio - (len(lineas)*25) - 10)
            can.save()
            packet.seek(0)
            return packet
        except: return None

    @staticmethod
    def crear_paginas_indice(entradas):
        paginas_pdf = []
        try:
            total_pags = math.ceil(len(entradas) / 30)
            for p in range(total_pags):
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                can.setFillColor(colors.black)
                can.setFont("Courier-Bold", 16)
                can.drawString(70, A4[1]-60, f"ÍNDICE DE CONTENIDOS (Pág. {p+1}/{total_pags})")
                can.setFont("Courier", 11)
                y = A4[1]-100
                for nombre, pag in entradas[p*30 : (p+1)*30]:
                    nombre_c = (nombre[:60] + '..') if len(nombre) > 60 else nombre
                    can.drawString(70, y, nombre_c)
                    can.drawRightString(A4[0]-70, y, str(pag))
                    y -= 20
                can.save()
                packet.seek(0)
                paginas_pdf.append(packet)
            return paginas_pdf
        except: return []

class AppPDF(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        self.title("PDF Fusion Ultimate v12.0 (Persistent)")
        self.geometry("750x980")
        ctk.set_appearance_mode("light")
        
        # Archivo de configuración
        self.config_file = "pdf_settings.json"
        
        self.archivos_finales = []
        self.ruta_guardado = os.path.join(os.path.expanduser("~"), "Documents")
        
        # Variables de estado
        self.check_indice = tk.BooleanVar(value=False)
        self.check_separadores = tk.BooleanVar(value=False)
        self.check_numeracion = tk.BooleanVar(value=False)
        self.check_compresion = tk.BooleanVar(value=False)
        self.var_dark_mode = tk.BooleanVar(value=False)
        self.current_theme = "XP"
        
        # --- CARGAR PREFERENCIAS ---
        self.load_settings()
        
        self.all_buttons = []
        self.init_ui()
        
        # Aplicar el tema cargado
        if self.var_dark_mode.get():
            self.apply_theme("DARK_PRO")
        else:
            self.apply_theme(self.current_theme)
        
        # Setup Drag & Drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.soltar_archivos)
        
        # GUARDAR AL CERRAR
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        """Carga la configuración desde el archivo JSON si existe"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.ruta_guardado = data.get("ruta", self.ruta_guardado)
                    self.check_indice.set(data.get("indice", False))
                    self.check_separadores.set(data.get("separadores", False))
                    self.check_numeracion.set(data.get("numeracion", False))
                    self.check_compresion.set(data.get("compresion", False))
                    self.var_dark_mode.set(data.get("dark_mode", False))
                    self.current_theme = data.get("theme", "XP")
            except Exception as e:
                print(f"Error cargando config: {e}")

    def on_close(self):
        """Guarda la configuración y cierra la app"""
        data = {
            "ruta": self.ruta_guardado,
            "indice": self.check_indice.get(),
            "separadores": self.check_separadores.get(),
            "numeracion": self.check_numeracion.get(),
            "compresion": self.check_compresion.get(),
            "dark_mode": self.var_dark_mode.get(),
            "theme": self.current_theme
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error guardando config: {e}")
        
        self.destroy()

    def init_ui(self):
        self.banner = ctk.CTkFrame(self, height=50)
        self.banner.pack(fill="x")
        
        self.lbl_title = ctk.CTkLabel(self.banner, text="  PDF FUSION ULTIMATE", font=("Arial", 13, "bold"))
        self.lbl_title.pack(side="left", padx=10)
        
        self.switch_dark = ctk.CTkSwitch(self.banner, text="Modo Oscuro", variable=self.var_dark_mode, 
                                         command=self.toggle_dark_mode, onvalue=True, offvalue=False,
                                         width=100, height=20, font=("Arial", 11, "bold"))
        self.switch_dark.pack(side="right", padx=15)

        self.btn_info = ctk.CTkButton(self.banner, text="?", width=25, height=25, command=self.mostrar_ayuda)
        self.btn_info.pack(side="right", padx=5)

        self.theme_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.theme_frame.pack(fill="x", pady=10)
        
        for t_name in ["XP", "LUMINOUS", "HACKER"]:
            btn = ctk.CTkButton(self.theme_frame, text=t_name, width=80, height=25, 
                                command=lambda n=t_name: self.set_base_theme(n))
            btn.pack(side="left", padx=5)
            self.all_buttons.append(btn)

        self.frame_top = ctk.CTkFrame(self, border_width=1)
        self.frame_top.pack(pady=5, padx=20, fill="x")
        self.btn_fold = self.crear_btn(self.frame_top, "Añadir Carpeta", self.seleccionar_carpeta, 180)
        self.btn_fold.pack(side="left", padx=15, pady=10)
        self.btn_files = self.crear_btn(self.frame_top, "Añadir Archivos", self.añadir_archivos, 180)
        self.btn_files.pack(side="left", padx=5, pady=10)

        self.frame_list_main = ctk.CTkFrame(self, border_width=2)
        self.frame_list_main.pack(pady=10, padx=20, fill="both", expand=True)
        self.frame_list_main.drop_target_register(DND_FILES)
        self.frame_list_main.dnd_bind('<<Drop>>', self.soltar_archivos)

        self.lbl_drop_hint = ctk.CTkLabel(self.frame_list_main, text="⬇ ARRASTRA TUS PDF AQUÍ ⬇", font=("Arial", 10, "bold"))
        self.lbl_drop_hint.pack(pady=(5,0))

        self.listbox = tk.Listbox(self.frame_list_main, borderwidth=0, highlightthickness=0)
        self.listbox.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.soltar_archivos)

        self.frame_ctrls = ctk.CTkFrame(self.frame_list_main)
        self.frame_ctrls.pack(side="right", fill="y")
        self.btn_up = self.crear_btn(self.frame_ctrls, "Subir", self.mover_subir, 70, 40)
        self.btn_up.pack(pady=5, padx=5)
        self.btn_down = self.crear_btn(self.frame_ctrls, "Bajar", self.mover_bajar, 70, 40)
        self.btn_down.pack(pady=5, padx=5)
        self.btn_del = self.crear_btn(self.frame_ctrls, "Borrar", self.eliminar_item, 70, 40)
        self.btn_del.pack(pady=20, padx=5)

        self.frame_opts = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opts.pack(pady=5, padx=20, fill="x")
        self.cb_idx = ctk.CTkCheckBox(self.frame_opts, text="Incluir Índice", variable=self.check_indice)
        self.cb_idx.pack(side="left", padx=10)
        self.cb_sep = ctk.CTkCheckBox(self.frame_opts, text="Páginas Separadoras", variable=self.check_separadores)
        self.cb_sep.pack(side="left", padx=10)
        
        self.frame_opts_2 = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opts_2.pack(pady=2, padx=20, fill="x")
        self.cb_num = ctk.CTkCheckBox(self.frame_opts_2, text="Numerar Capítulos", variable=self.check_numeracion)
        self.cb_num.pack(side="left", padx=10)
        self.cb_comp = ctk.CTkCheckBox(self.frame_opts_2, text="Compresión (Optimizar)", variable=self.check_compresion)
        self.cb_comp.pack(side="left", padx=10)

        self.frame_save = ctk.CTkFrame(self, border_width=1)
        self.frame_save.pack(pady=5, padx=20, fill="x")
        self.lbl_ruta_dest = ctk.CTkLabel(self.frame_save, text=f"Destino: {self.ruta_guardado}")
        self.lbl_ruta_dest.pack(side="left", padx=15, pady=5)
        self.btn_dest = self.crear_btn(self.frame_save, "Cambiar...", self.cambiar_destino, 100)
        self.btn_dest.pack(side="right", padx=10, pady=5)

        self.entry_nombre = ctk.CTkEntry(self, width=450, placeholder_text="Nombre del archivo final...")
        self.entry_nombre.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.set(0)
        self.progress.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Sistema listo")
        self.lbl_status.pack()

        self.btn_run = self.crear_btn(self, ">> EJECUTAR FUSIÓN <<", self.iniciar_hilo_fusion, 400, 60)
        self.btn_run.pack(pady=20)

    def crear_btn(self, master, texto, comando, ancho, alto=35):
        btn = ctk.CTkButton(master, text=texto, command=comando, width=ancho, height=alto)
        self.all_buttons.append(btn)
        return btn

    def set_base_theme(self, theme_name):
        self.current_theme = theme_name
        if not self.var_dark_mode.get():
            self.apply_theme(theme_name)

    def toggle_dark_mode(self):
        if self.var_dark_mode.get():
            self.apply_theme("DARK_PRO")
        else:
            self.apply_theme(self.current_theme)

    def apply_theme(self, theme_name):
        c = THEMES[theme_name]
        self.configure(fg_color=c["bg"])
        self.banner.configure(fg_color=c["accent"])
        
        text_col = "white" if theme_name != "HACKER" else c["text"]
        self.lbl_title.configure(text_color=text_col)
        self.switch_dark.configure(text_color=text_col, progress_color="white")

        for f in [self.frame_top, self.frame_list_main, self.frame_save]:
            f.configure(fg_color=c["container"], border_color=c["border"], corner_radius=c["radius"])
        
        self.listbox.configure(bg=c["list_bg"], fg=c["text"], selectbackground=c["accent"], font=(c["font"], 10))
        self.lbl_status.configure(text_color=c["accent"], font=(c["font"], 10, "italic"))
        self.entry_nombre.configure(fg_color=c["list_bg"], text_color=c["text"], border_color=c["border"], corner_radius=c["radius"])
        self.lbl_drop_hint.configure(text_color=c["border"])
        
        for lbl in [self.lbl_ruta_dest]:
             lbl.configure(text_color=c["text"], font=(c["font"], 9))

        for cb in [self.cb_idx, self.cb_sep, self.cb_num, self.cb_comp]:
            cb.configure(text_color=c["text"], font=(c["font"], 11), border_color=c["border"])

        for b in self.all_buttons:
            is_run = (b == self.btn_run)
            b.configure(
                fg_color=c["btn_run"] if is_run else c["btn"],
                text_color="white" if theme_name != "HACKER" or is_run else c["text"],
                border_color=c["border"], border_width=1,
                corner_radius=c["radius"], font=(c["font"], 12, "bold")
            )
        self.btn_info.configure(fg_color="#D1D1D1" if theme_name == "XP" else c["btn"], 
                                text_color="black" if theme_name == "XP" else "white")

    def soltar_archivos(self, event):
        try:
            files = re.findall(r'\{.*?\}|\S+', event.data)
            valid_files = []
            for f in files:
                clean_path = f.strip('{} ')
                if clean_path.lower().endswith('.pdf'):
                    valid_files.append(clean_path)

            if valid_files:
                self.archivos_finales.extend(valid_files)
                self.actualizar_listbox()
                self.lbl_status.configure(text=f"✅ {len(valid_files)} PDFs añadidos")
            else:
                self.lbl_status.configure(text="⚠️ El archivo arrastrado no parece un PDF")
        except Exception as e:
            messagebox.showerror("Error", f"Error al soltar: {e}")

    def mostrar_ayuda(self):
        msg = "1. Añade PDFs (Botones o arrastrando).\n2. Configura opciones (Se guardan al salir).\n3. Pulsa Ejecutar."
        messagebox.showinfo("Ayuda v12.0", msg)

    def seleccionar_carpeta(self):
        f = filedialog.askdirectory()
        if f:
            self.archivos_finales.extend(sorted([os.path.join(f, x) for x in os.listdir(f) if x.lower().endswith('.pdf')]))
            self.actualizar_listbox()

    def añadir_archivos(self):
        fs = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if fs:
            self.archivos_finales.extend(list(fs))
            self.actualizar_listbox()

    def actualizar_listbox(self):
        self.listbox.delete(0, tk.END)
        for f in self.archivos_finales: self.listbox.insert(tk.END, f" {os.path.basename(f)}")

    def eliminar_item(self):
        sel = self.listbox.curselection()
        if sel: del self.archivos_finales[sel[0]]; self.actualizar_listbox()

    def mover_subir(self):
        idx = self.listbox.curselection()
        if idx and idx[0] > 0:
            i = idx[0]; self.archivos_finales[i], self.archivos_finales[i-1] = self.archivos_finales[i-1], self.archivos_finales[i]
            self.actualizar_listbox(); self.listbox.select_set(i-1)

    def mover_bajar(self):
        idx = self.listbox.curselection()
        if idx and idx[0] < len(self.archivos_finales)-1:
            i = idx[0]; self.archivos_finales[i], self.archivos_finales[i+1] = self.archivos_finales[i+1], self.archivos_finales[i]
            self.actualizar_listbox(); self.listbox.select_set(i+1)

    def cambiar_destino(self):
        n = filedialog.askdirectory(); self.ruta_guardado = n if n else self.ruta_guardado
        self.lbl_ruta_dest.configure(text=f"Destino: {self.ruta_guardado}")

    def iniciar_hilo_fusion(self):
        if not self.archivos_finales:
            messagebox.showwarning("Aviso", "No hay archivos en la lista.")
            return
        threading.Thread(target=self.procesar, daemon=True).start()

    def obtener_nombre_seguro(self, carpeta, nombre_base):
        nombre_final = nombre_base if nombre_base.lower().endswith(".pdf") else nombre_base + ".pdf"
        ruta = os.path.join(carpeta, nombre_final)
        c = 1
        while os.path.exists(ruta):
            ruta = os.path.join(carpeta, f"{os.path.splitext(nombre_final)[0]} ({c}).pdf")
            c += 1
        return ruta

    def procesar(self):
        out_path = self.obtener_nombre_seguro(self.ruta_guardado, self.entry_nombre.get().strip() or "Resultado")
        inc_idx, inc_seps = self.check_indice.get(), self.check_separadores.get()
        do_num = self.check_numeracion.get()
        do_comp = self.check_compresion.get()
        
        fallidos = []
        try:
            self.after(0, lambda: self.btn_run.configure(state="disabled", text="OPTIMIZANDO Y FUSIONANDO..."))
            writer = PdfWriter()
            entries = []
            curr_p = (math.ceil(len(self.archivos_finales) / 30) if inc_idx else 0) + 1
            
            for i, path in enumerate(self.archivos_finales):
                try:
                    reader = PdfReader(path)
                    base_name = os.path.basename(path)
                    display_name = f"{i+1:02d}. {base_name}" if do_num else base_name
                    entries.append((path, curr_p, display_name))
                    curr_p += (1 if inc_seps else 0) + len(reader.pages)
                except: fallidos.append(os.path.basename(path))

            if inc_idx:
                data_idx = [(item[2], item[1]) for item in entries]
                for p_s in PDFLogic.crear_paginas_indice(data_idx):
                    writer.append(PdfReader(p_s))

            for i, (path, p_start, display_name) in enumerate(entries):
                self.after(0, lambda t=f"Procesando: {display_name}": self.lbl_status.configure(text=t))
                if inc_seps: 
                    sep = PDFLogic.crear_separador(display_name)
                    if sep: writer.append(PdfReader(sep))
                writer.add_outline_item(display_name, p_start - 1)
                writer.append(path)
                self.after(0, lambda v=(i+1)/len(entries): self.progress.set(v))

            if do_comp:
                self.after(0, lambda: self.lbl_status.configure(text="Comprimiendo archivo final... (Espere)"))
                writer.compress_identical_objects(remove_identicals=True)
                for page in writer.pages:
                    page.compress_content_streams()

            with open(out_path, "wb") as f: writer.write(f)
            self.after(0, lambda: self.finalizar(out_path, fallidos))
            
        except Exception as e: 
            self.after(0, lambda msg=str(e): messagebox.showerror("Error Crítico", msg))
        finally: 
            self.after(0, lambda: self.btn_run.configure(state="normal", text=">> EJECUTAR FUSIÓN <<"))

    def finalizar(self, ruta, fallos):
        subprocess.Popen(f'explorer /select,"{os.path.normpath(ruta)}"')
        self.lbl_status.configure(text="✅ PDF LISTO")
        if fallos: messagebox.showwarning("Aviso", f"Omitidos por error:\n" + "\n".join(fallos))
        self.archivos_finales = []; self.actualizar_listbox(); self.entry_nombre.delete(0, tk.END); self.progress.set(0)

if __name__ == "__main__":
    app = AppPDF()
    app.mainloop()