import sqlite3
import os
from flask import (Flask, g, render_template, request, redirect, url_for,
                   flash) # Añadir flash

app = Flask(__name__)
# Necesitas una 'secret_key' para usar flash
app.config['SECRET_KEY'] = os.urandom(24) # Clave secreta para mensajes flash

# --- Configuración de la Base de Datos (igual que antes) ---
DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'peliculas.db')
os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Rutas ---

@app.route('/')
def index():
    """
    Ruta principal que muestra el formulario y todas las películas.
    """
    db = get_db()
    # Ordenamos por ID descendente para ver las más nuevas primero (opcional)
    cursor = db.execute('SELECT id, title, director, year, genre FROM movie ORDER BY id DESC')
    peliculas = cursor.fetchall()
    # Renderiza index.html y le pasa la lista de películas
    return render_template('index.html', peliculas=peliculas)

@app.route('/add', methods=['POST']) # Solo maneja POST
def add_movie():
    """
    Procesa la adición de una nueva película desde el formulario en index.html.
    """
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form['year']
        genre = request.form['genre']

        error = None
        if not title: error = 'Título es requerido.'
        elif not director: error = 'Director es requerido.'
        elif not year: error = 'Año es requerido.'
        elif not genre: error = 'Género es requerido.'

        if error is None:
            try:
                year_int = int(year) # Intenta convertir a entero
                db = get_db()
                db.execute(
                    'INSERT INTO movie (title, director, year, genre) VALUES (?, ?, ?, ?)',
                    (title, director, year_int, genre)
                )
                db.commit()
                flash('¡Película añadida correctamente!', 'success') # Mensaje de éxito
            except ValueError:
                error = 'El año debe ser un número válido.'
            except sqlite3.Error as e:
                 error = f"Error en la base de datos: {e}"

        if error:
            flash(f'Error al añadir película: {error}', 'error') # Mensaje de error

        # Siempre redirige a index después de intentar añadir
        return redirect(url_for('index'))

    # Si alguien intenta acceder a /add via GET (no debería pasar con methods=['POST'])
    # podrías redirigir o mostrar un error. Por simplicidad, solo redirigimos.
    return redirect(url_for('index'))


# --- Inicialización (igual que antes) ---
def init_db():
    db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        print("Intentando crear tabla 'movie'...")
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                director TEXT NOT NULL,
                year INTEGER NOT NULL,
                genre TEXT NOT NULL
            );
        """)
        db.commit()
        print("Tabla 'movie' verificada/creada.")
    except sqlite3.Error as e:
        print(f"Error al crear tabla: {e}")
    finally:
        db.close()

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('Base de datos inicializada.')


if __name__ == '__main__':
    app.run(debug=True)
