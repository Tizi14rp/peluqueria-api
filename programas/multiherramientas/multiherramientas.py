import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- LÓGICA DE BASE DE DATOS LOCAL (Archivos JSON) ---
def cargar_db(archivo):
    if not os.path.exists(archivo):
        return []
    with open(archivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_db(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4)

def resetear_db(archivo, callback):
    if messagebox.askyesno("Resetear", f"¿Seguro que deseas borrar todos los datos?"):
        if os.path.exists(archivo):
            os.remove(archivo)
        callback()

def borrar_registro_individual(archivo, index, callback):
    db = cargar_db(archivo)
    if 0 <= index < len(db):
        del db[index]
        guardar_db(archivo, db)
        callback()

# --- APLICACIÓN PRINCIPAL ---
class MiAppMultiherramienta(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mi App de Gestión")
        self.geometry("950x700")
        self.configure(bg="#f3f4f6")
        
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook', background='#f3f4f6')
        style.configure('TNotebook.Tab', padding=[15, 10], font=('Helvetica', 10, 'bold'))
        style.configure('TFrame', background='#ffffff')
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('Danger.TButton', foreground='red')
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.crear_pestaña_notas()
        self.crear_pestaña_finanzas()
        self.crear_pestaña_facturas()
        self.crear_pestaña_turnos()
        self.crear_pestaña_tareas()
        self.crear_pestaña_stock()

    # --- 1. NOTAS ---
    def crear_pestaña_notas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📝 Notas')
        ttk.Label(frame, text="Escribe una nota nueva:", font=('Helvetica', 10), background='white').pack(pady=(10,0), padx=20, anchor='w')
        self.nota_texto = tk.Text(frame, height=4, width=80, font=('Helvetica', 10))
        self.nota_texto.pack(pady=5, padx=20)
        btn_frame = ttk.Frame(frame); btn_frame.pack(fill='x', padx=20, pady=5)
        ttk.Button(btn_frame, text="Guardar Nota", command=self.guardar_nota).pack(side='left')
        ttk.Button(btn_frame, text="Resetear", style='Danger.TButton', command=lambda: resetear_db('notas.json', self.actualizar_notas)).pack(side='right')
        self.lista_notas = tk.Listbox(frame, font=('Helvetica', 11))
        self.lista_notas.pack(fill='both', expand=True, padx=20, pady=10)
        self.lista_notas.bind('<Double-1>', lambda e: self.borrar_item('notas.json', self.lista_notas, self.actualizar_notas))
        self.actualizar_notas()

    def guardar_nota(self):
        texto = self.nota_texto.get("1.0", "end-1c").strip()
        if texto:
            db = cargar_db('notas.json'); db.append({"texto": texto}); guardar_db('notas.json', db)
            self.nota_texto.delete("1.0", "end"); self.actualizar_notas()

    def actualizar_notas(self):
        self.lista_notas.delete(0, tk.END)
        for nota in cargar_db('notas.json'): self.lista_notas.insert(tk.END, f"❌ {nota['texto']}")

    # --- 2. FINANZAS ---
    def crear_pestaña_finanzas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='💰 Finanzas')
        inf = ttk.Frame(frame); inf.pack(fill='x', padx=20, pady=10)
        ttk.Label(inf, text="Descripción:", background='white').grid(row=0, column=0)
        self.fin_desc = ttk.Entry(inf, width=20); self.fin_desc.grid(row=0, column=1, padx=5)
        ttk.Label(inf, text="Monto:", background='white').grid(row=0, column=2)
        self.fin_monto = ttk.Entry(inf, width=10); self.fin_monto.grid(row=0, column=3, padx=5)
        self.fin_tipo = ttk.Combobox(inf, values=["Ingreso", "Gasto"], state="readonly", width=10)
        self.fin_tipo.current(0); self.fin_tipo.grid(row=0, column=4, padx=5)
        ttk.Button(inf, text="Registrar", command=self.guardar_finanza).grid(row=0, column=5, padx=5)
        ttk.Button(inf, text="Reset", style='Danger.TButton', command=lambda: resetear_db('finanzas.json', self.actualizar_finanzas)).grid(row=0, column=6)
        self.canvas = tk.Canvas(frame, height=150, bg='white'); self.canvas.pack(fill='x', padx=20, pady=5)
        self.lista_finanzas = tk.Listbox(frame, font=('Helvetica', 10))
        self.lista_finanzas.pack(fill='both', expand=True, padx=20, pady=5)
        self.lista_finanzas.bind('<Double-1>', lambda e: self.borrar_item('finanzas.json', self.lista_finanzas, self.actualizar_finanzas))
        self.actualizar_finanzas()

    def guardar_finanza(self):
        desc, monto = self.fin_desc.get(), self.fin_monto.get()
        if desc and monto.replace('.', '', 1).isdigit():
            db = cargar_db('finanzas.json'); db.append({"desc": desc, "monto": float(monto), "tipo": self.fin_tipo.get()})
            guardar_db('finanzas.json', db); self.fin_desc.delete(0, 'end'); self.fin_monto.delete(0, 'end'); self.actualizar_finanzas()

    def actualizar_finanzas(self):
        self.lista_finanzas.delete(0, tk.END)
        db = cargar_db('finanzas.json')
        ing, gas = sum(f['monto'] for f in db if f['tipo'] == 'Ingreso'), sum(f['monto'] for f in db if f['tipo'] == 'Gasto')
        for f in db: self.lista_finanzas.insert(tk.END, f"❌ {'+' if f['tipo'] == 'Ingreso' else '-'} ${f['monto']:.2f} | {f['desc']}")
        self.canvas.delete("all")
        m = max(ing, gas, 1)
        self.canvas.create_rectangle(50, 130 - (ing/m*100), 150, 130, fill="#10B981")
        self.canvas.create_text(100, 140, text=f"Ingresos: ${ing}")
        self.canvas.create_rectangle(200, 130 - (gas/m*100), 300, 130, fill="#EF4444")
        self.canvas.create_text(250, 140, text=f"Gastos: ${gas}")

    # --- 3. FACTURAS ---
    def crear_pestaña_facturas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🧾 Facturas')
        inf = ttk.Frame(frame); inf.pack(fill='x', padx=20, pady=10)
        ttk.Label(inf, text="Cliente:", background='white').grid(row=0, column=0)
        self.fac_cliente = ttk.Entry(inf, width=15); self.fac_cliente.grid(row=0, column=1, padx=5)
        ttk.Label(inf, text="Detalle:", background='white').grid(row=0, column=2)
        self.fac_detalle = ttk.Entry(inf, width=20); self.fac_detalle.grid(row=0, column=3, padx=5)
        ttk.Label(inf, text="Total $:", background='white').grid(row=0, column=4)
        self.fac_total = ttk.Entry(inf, width=10); self.fac_total.grid(row=0, column=5, padx=5)
        ttk.Button(inf, text="Generar", command=self.guardar_factura).grid(row=0, column=6, padx=5)
        ttk.Button(inf, text="Reset", style='Danger.TButton', command=lambda: resetear_db('facturas.json', self.actualizar_facturas)).grid(row=0, column=7)
        self.lista_fac = tk.Listbox(frame, font=('Helvetica', 11))
        self.lista_fac.pack(fill='both', expand=True, padx=20, pady=10)
        self.lista_fac.bind('<Double-1>', lambda e: self.borrar_item('facturas.json', self.lista_fac, self.actualizar_facturas))
        self.actualizar_facturas()

    def guardar_factura(self):
        cli, det, tot = self.fac_cliente.get(), self.fac_detalle.get(), self.fac_total.get()
        if cli and tot:
            db = cargar_db('facturas.json')
            import random
            db.append({"id": f"F-{random.randint(100,999)}", "cliente": cli, "detalle": det, "total": tot})
            guardar_db('facturas.json', db)
            self.fac_cliente.delete(0, 'end'); self.fac_detalle.delete(0, 'end'); self.fac_total.delete(0, 'end')
            self.actualizar_facturas()

    def actualizar_facturas(self):
        self.lista_fac.delete(0, tk.END)
        for f in cargar_db('facturas.json'): 
            # SE AGREGÓ f['detalle'] AQUÍ ABAJO:
            self.lista_fac.insert(tk.END, f"❌ {f['id']} | {f['cliente']} - {f['detalle']} - ${f['total']}")

    # --- 4. TURNOS ---
    def crear_pestaña_turnos(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📅 Turnos')
        inf = ttk.Frame(frame); inf.pack(fill='x', padx=20, pady=10)
        ttk.Label(inf, text="Nombre:", background='white').pack(side='left')
        self.tur_nom = ttk.Entry(inf, width=20); self.tur_nom.pack(side='left', padx=5)
        ttk.Label(inf, text="Fecha/Hora:", background='white').pack(side='left')
        self.tur_fec = ttk.Entry(inf, width=15); self.tur_fec.pack(side='left', padx=5)
        ttk.Button(inf, text="Agendar", command=self.guardar_turno).pack(side='left', padx=5)
        ttk.Button(inf, text="Reset", style='Danger.TButton', command=lambda: resetear_db('turnos.json', self.actualizar_turnos)).pack(side='right')
        self.lista_tur = tk.Listbox(frame, font=('Helvetica', 11))
        self.lista_tur.pack(fill='both', expand=True, padx=20, pady=10)
        self.lista_tur.bind('<Double-1>', lambda e: self.borrar_item('turnos.json', self.lista_tur, self.actualizar_turnos))
        self.actualizar_turnos()

    def guardar_turno(self):
        n, f = self.tur_nom.get(), self.tur_fec.get()
        if n and f:
            db = cargar_db('turnos.json'); db.append({"nombre": n, "fecha": f}); guardar_db('turnos.json', db)
            self.tur_nom.delete(0, 'end'); self.tur_fec.delete(0, 'end'); self.actualizar_turnos()

    def actualizar_turnos(self):
        self.lista_tur.delete(0, tk.END)
        for t in cargar_db('turnos.json'): self.lista_tur.insert(tk.END, f"❌ {t['fecha']} -> {t['nombre']}")

    # --- 5. TAREAS ---
    def crear_pestaña_tareas(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='☑️ Tareas')
        inf = ttk.Frame(frame); inf.pack(fill='x', padx=20, pady=10)
        ttk.Label(inf, text="Nueva Tarea:", background='white').pack(side='left')
        self.tar_txt = ttk.Entry(inf, width=40); self.tar_txt.pack(side='left', padx=5)
        ttk.Button(inf, text="Agregar", command=self.guardar_tarea).pack(side='left')
        ttk.Button(inf, text="Reset", style='Danger.TButton', command=lambda: resetear_db('tareas.json', self.actualizar_tareas)).pack(side='right')
        self.lista_tar = tk.Listbox(frame, font=('Helvetica', 12))
        self.lista_tar.pack(fill='both', expand=True, padx=20, pady=10)
        self.lista_tar.bind('<Double-1>', lambda e: self.borrar_item('tareas.json', self.lista_tar, self.actualizar_tareas))
        self.actualizar_tareas()

    def guardar_tarea(self):
        t = self.tar_txt.get()
        if t:
            db = cargar_db('tareas.json'); db.append({"tarea": t}); guardar_db('tareas.json', db)
            self.tar_txt.delete(0, 'end'); self.actualizar_tareas()

    def actualizar_tareas(self):
        self.lista_tar.delete(0, tk.END)
        for t in cargar_db('tareas.json'): self.lista_tar.insert(tk.END, f"❌ {t['tarea']}")

    # --- 6. STOCK ---
    def crear_pestaña_stock(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📦 Stock')
        inf = ttk.Frame(frame); inf.pack(fill='x', padx=20, pady=10)
        ttk.Label(inf, text="Producto:", background='white').grid(row=0, column=0)
        self.stk_prod = ttk.Entry(inf, width=15); self.stk_prod.grid(row=0, column=1, padx=2)
        ttk.Label(inf, text="Cant:", background='white').grid(row=0, column=2)
        self.stk_cant = ttk.Entry(inf, width=5); self.stk_cant.grid(row=0, column=3, padx=2)
        ttk.Label(inf, text="Mín:", background='white').grid(row=0, column=4)
        self.stk_min = ttk.Entry(inf, width=5); self.stk_min.grid(row=0, column=5, padx=2)
        ttk.Button(inf, text="Añadir", command=self.guardar_stock).grid(row=0, column=6, padx=5)
        ttk.Button(inf, text="Reset", style='Danger.TButton', command=lambda: resetear_db('stock.json', self.actualizar_stock)).grid(row=0, column=7)
        self.lista_stk = tk.Listbox(frame, font=('Helvetica', 11))
        self.lista_stk.pack(fill='both', expand=True, padx=20, pady=10)
        self.lista_stk.bind('<Double-1>', lambda e: self.borrar_item('stock.json', self.lista_stk, self.actualizar_stock))
        self.actualizar_stock()

    def guardar_stock(self):
        p, c, m = self.stk_prod.get(), self.stk_cant.get(), self.stk_min.get()
        if p and c.isdigit():
            db = cargar_db('stock.json'); db.append({"prod": p, "cant": int(c), "min": int(m)})
            guardar_db('stock.json', db); self.stk_prod.delete(0, 'end'); self.stk_cant.delete(0, 'end'); self.actualizar_stock()

    def actualizar_stock(self):
        self.lista_stk.delete(0, tk.END)
        for s in cargar_db('stock.json'):
            a = " ⚠️" if s['cant'] <= s.get('min', 0) else ""
            self.lista_stk.insert(tk.END, f"❌ {s['prod']} - Cant: {s['cant']}{a}")

    def borrar_item(self, archivo, listbox, callback):
        sel = listbox.curselection()
        if sel and messagebox.askyesno("Borrar", "¿Eliminar este registro?"):
            borrar_registro_individual(archivo, sel[0], callback)

if __name__ == "__main__":
    app = MiAppMultiherramienta()
    app.mainloop()