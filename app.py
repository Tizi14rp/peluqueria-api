from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app) # Permite que el HTML conecte con este servidor

# ... (mantén tus imports y la configuración de Flask/CORS arriba)

# Conexión a la memoria
conn = sqlite3.connect('peluqueria.db', check_same_thread=False)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    if 'id' in d:
        d['_id'] = str(d['id'])
    return d

conn.row_factory = dict_factory

# --- SOLUCIÓN: Crear tablas directamente ---
cursor = conn.cursor()
cursor.executescript('''
CREATE TABLE IF NOT EXISTS turnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    servicio TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS caja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    monto REAL NOT NULL,
    descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS estadisticas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,
    nombre TEXT NOT NULL,
    valor INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cortes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    url_imagen TEXT NOT NULL
);
''')
conn.commit()
print("✅ Tablas creadas correctamente en la memoria.")

# ... (mantén el resto de tus rutas @app.route abajo)

# Formatear las respuestas de SQLite como diccionarios
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    if 'id' in d:
        d['_id'] = str(d['id']) # Mapeo de ID compatible con tu frontend original
    return d

conn.row_factory = dict_factory

# --- RUTAS DE LA API ---

@app.route('/api/<tabla>', methods=['GET', 'POST', 'DELETE'])
def manejar_tabla(tabla):
    tablas_validas = ['turnos', 'caja', 'estadisticas', 'cortes']
    if tabla not in tablas_validas:
        return jsonify({'error': 'Tabla no válida'}), 400
    
    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute(f"SELECT * FROM {tabla}")
        datos = cur.fetchall()
        return jsonify(datos)
        
    elif request.method == 'POST':
        data = request.json
        print(f"Recibiendo datos para {tabla}: {data}") # Esto aparecerá en tu terminal
        columnas = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        valores = tuple(data.values())
        try:
            cur.execute(f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})", valores)
            conn.commit()
            return jsonify({'status': 'success'}), 201
        except Exception as e:
            print(f"Error al insertar: {e}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'DELETE':
        cur.execute(f"DELETE FROM {tabla}")
        conn.commit()
        return jsonify({'message': 'Borrados todos'})

@app.route('/api/<tabla>/<int:id>', methods=['DELETE', 'PUT'])
def manejar_item(tabla, id):
    tablas_validas = ['turnos', 'caja', 'estadisticas', 'cortes']
    if tabla not in tablas_validas:
        return jsonify({'error': 'Tabla no válida'}), 400

    cur = conn.cursor()

    if request.method == 'DELETE':
        cur.execute(f"DELETE FROM {tabla} WHERE id = ?", (id,))
        conn.commit()
        return jsonify({'message': 'Registro borrado exitosamente'})
        
    elif request.method == 'PUT' and tabla == 'turnos':
        data = request.json
        if 'cliente' in data:
            cur.execute("UPDATE turnos SET cliente = ? WHERE id = ?", (data['cliente'], id))
            conn.commit()
        return jsonify({'message': 'Turno actualizado exitosamente'})

if __name__ == '__main__':
    import os
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)