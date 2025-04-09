import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, abort
# Importamos 'db' y 'Movie' desde models.py (asegúrate que models.py tiene db = SQLAlchemy())
from models import db, Movie
import requests
import random

# --- Configuración Inicial ---
# 'app' se define aquí para poder usar app.instance_path después
app = Flask(__name__, instance_relative_config=False) # instance_relative_config=False es el valor por defecto, pero lo ponemos por claridad

# ¡IMPORTANTE! Cambia esto por una clave secreta real y segura
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura_123!'

# --- Configuración de la Base de Datos (CORREGIDA para carpeta instance) ---
instance_path = app.instance_path # Obtiene la ruta absoluta a la carpeta 'instance'

# Opcional: Asegura que la carpeta 'instance' exista
# try:
#     os.makedirs(instance_path, exist_ok=True)
# except OSError as e:
#     print(f"Error creando la carpeta instance: {e}") # Manejo básico de error

db_path = os.path.join(instance_path, 'movies.db') # Ruta completa al archivo
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Imprime la ruta para verificar (Mantenlo temporalmente) ---
print(f"--- [INFO] Configurando SQLAlchemy ---")
print(f"--- [INFO] Ruta de instancia: {instance_path} ---")
print(f"--- [INFO] Intentando usar DB en: {db_path} ---")
print(f"--- [INFO] ¿Existe el archivo DB? {os.path.exists(db_path)} ---")
# ----------------------------------------------------------------

# --- Inicializa la extensión SQLAlchemy con la app ---
# 'db' viene de models.py
try:
    db.init_app(app)
    print("--- [INFO] SQLAlchemy inicializado con la app. ---")
except Exception as e:
    print(f"--- [ERROR] Falló db.init_app(app): {e} ---")


# --- Clave API y URLs (Para Postman y carrusel) ---
API_KEY = '0793a5c442c049e9b0321cf71326063b' # Tu clave TMDb
BASE_URL = 'https://api.themoviedb.org/3/'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w342'

# --- Base de datos EN MEMORIA (para rutas originales /movies de Postman) ---
movies_db_memory = []

# --- Rutas ORIGINALES (Para Postman, usan API externa y movies_db_memory) ---
# Estas rutas NO usan la base de datos real 'movies.db'

@app.route('/movies', methods=['POST'])
def add_movie_api():
    title = request.json.get('title')
    if not title: return jsonify({'error': 'El título es obligatorio'}), 400

    try:
        response = requests.get(f'{BASE_URL}search/movie', params={'query': title, 'api_key': API_KEY, 'language': 'es-ES'}, timeout=10)
        response.raise_for_status() # Lanza error para 4xx/5xx
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al conectar con la API externa: {e}'}), 500

    data = response.json()
    if data.get('results'):
        movie_data = data['results'][0]
        movie = {
            'id': len(movies_db_memory) + 1,
            'title': movie_data.get('title', 'N/A'),
            'year': movie_data.get('release_date', 'N/A')[:4],
            'genre': 'N/A',
            'plot': movie_data.get('overview', 'N/A')
        }
        movies_db_memory.append(movie)
        return jsonify(movie), 201
    else:
        return jsonify({'error': 'Pelicula no encontrada en API externa'}), 404

@app.route('/movies', methods=['GET'])
def get_movies_api():
    return jsonify(movies_db_memory)

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_api(movie_id):
    movie = next((m for m in movies_db_memory if m['id'] == movie_id), None)
    if not movie: return jsonify({'error': 'Pelicula no encontrada en memoria'}), 404
    return jsonify(movie)

@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie_api(movie_id):
    movie = next((m for m in movies_db_memory if m['id'] == movie_id), None)
    if not movie: return jsonify({'error': 'Pelicula no encontrada en memoria'}), 404
    data = request.json
    movie['title'] = data.get('title', movie['title'])
    movie['year'] = data.get('year', movie['year'])
    movie['genre'] = data.get('genre', movie['genre'])
    movie['plot'] = data.get('plot', movie['plot'])
    return jsonify(movie)

# Ruta /movies/edit/<id> original - Parece incompleta/sin uso real
@app.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie_original(movie_id):
    movie = next((m for m in movies_db_memory if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Película no encontrada en memoria (ruta original)'}), 404
    return jsonify(movie) # Simplemente devuelve JSON


@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie_api(movie_id):
    global movies_db_memory
    initial_len = len(movies_db_memory)
    movies_db_memory = [m for m in movies_db_memory if m['id'] != movie_id]
    if len(movies_db_memory) == initial_len: return jsonify({'error': 'Pelicula no encontrada en memoria'}), 404
    return jsonify({'message': 'Pelicula eliminada de memoria'}), 200


# --- Rutas NUEVAS (Para Frontend, usan movies.db real) ---

@app.route('/')
def index():
    print("--- [DEBUG] Entrando a la ruta '/' ---")
    # Datos para el Carrusel (desde API externa)
    peliculas_api_carousel = []
    try:
        response = requests.get(f'{BASE_URL}movie/popular', params={'api_key': API_KEY, 'language': 'es-ES'}, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        num_samples = min(5, len(results))
        peliculas_api_carousel = random.sample(results, num_samples) if num_samples > 0 else []
        for pelicula in peliculas_api_carousel:
            poster_path = pelicula.get('poster_path')
            pelicula['poster_url'] = f'{IMAGE_BASE_URL}{poster_path}' if poster_path else url_for('static', filename='images/default_poster.png')
        print(f"--- [DEBUG] {len(peliculas_api_carousel)} películas obtenidas de la API para el carrusel.")
    except requests.exceptions.RequestException as e:
        flash(f'Error al cargar populares: {e}', 'warning')
        print(f"--- [ERROR] Falló la llamada API para el carrusel: {e} ---")
    except Exception as e:
        flash(f'Error inesperado cargando populares: {e}', 'danger')
        print(f"--- [ERROR] Error inesperado en la llamada API para el carrusel: {e} ---")

    # Datos para la Lista (desde Base de Datos local 'movies.db')
    lista_peliculas_db = []
    try:
        print("--- [DEBUG] Intentando consultar la base de datos local... ---")
        lista_peliculas_db = Movie.query.order_by(Movie.title).all()
        print(f"--- [DEBUG] {len(lista_peliculas_db)} películas obtenidas de la base de datos local.")
    except Exception as e:
        flash(f'Error al leer la colección local: ({type(e).__name__})', 'danger')
        # Imprime el error completo en la consola para depuración
        print(f"--- [ERROR] Falló la consulta a la base de datos: {e} ---")
        import traceback
        traceback.print_exc() # Imprime el traceback completo

    # Renderizar plantilla
    print("--- [DEBUG] Renderizando plantilla index.html... ---")
    return render_template('index.html',
                        peliculas_api=peliculas_api_carousel,
                        peliculas_db=lista_peliculas_db)

# Añadir película a la BD (desde formulario frontend)
@app.route('/collection/add', methods=['POST'])
def add_movie_db():
    print("--- [DEBUG] Recibida petición POST a /collection/add ---")
    title = request.form.get('title')
    director = request.form.get('director')
    year_str = request.form.get('year')
    genre = request.form.get('genre')
    print(f"--- [DEBUG] Datos recibidos: Title={title}, Director={director}, Year={year_str}, Genre={genre}")
    if not all([title, director, year_str, genre]):
        flash('Todos los campos son obligatorios.', 'warning')
        print("--- [DEBUG] Faltan campos en el formulario de añadir. Redirigiendo.")
    else:
        try:
            year = int(year_str)
            nueva_pelicula = Movie(title=title, director=director, year=year, genre=genre)
            print(f"--- [DEBUG] Creando objeto Movie: {nueva_pelicula}")
            db.session.add(nueva_pelicula)
            db.session.commit()
            print("--- [DEBUG] Película añadida a la BD y commit realizado.")
            flash('Película añadida a tu colección.', 'success')
        except ValueError:
            flash('El año debe ser un número válido.', 'warning')
            print("--- [ERROR] Error de ValueError al convertir año.")
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar en la base de datos ({type(e).__name__})', 'danger')
            print(f"--- [ERROR] Error al guardar en BD: {e}. Rollback realizado.")
            import traceback
            traceback.print_exc()
    return redirect(url_for('index'))


# Mostrar formulario para editar película de la BD
@app.route('/collection/edit/<int:movie_id>', methods=['GET'])
def edit_movie_db_form(movie_id):
    print(f"--- [DEBUG] Recibida petición GET a /collection/edit/{movie_id} ---")
    # get_or_404 maneja el caso de no encontrar la película
    movie = db.get_or_404(Movie, movie_id, description=f"No se encontró película con ID {movie_id}")
    print(f"--- [DEBUG] Película encontrada para editar: {movie}")
    return render_template('edit_movie.html', movie=movie)


# Actualizar película en la BD (desde formulario de edición)
@app.route('/collection/update/<int:movie_id>', methods=['POST'])
def update_movie_db(movie_id):
    print(f"--- [DEBUG] Recibida petición POST a /collection/update/{movie_id} ---")
    movie = db.get_or_404(Movie, movie_id, description=f"No se encontró película con ID {movie_id} para actualizar")
    print(f"--- [DEBUG] Película encontrada para actualizar: {movie}")
    try:
        # Obtener datos del formulario
        new_title = request.form.get('title')
        new_director = request.form.get('director')
        new_year_str = request.form.get('year')
        new_genre = request.form.get('genre')
        print(f"--- [DEBUG] Datos recibidos para actualizar: Title={new_title}, Director={new_director}, Year={new_year_str}, Genre={new_genre}")

        # Validar año antes de actualizar
        year = int(new_year_str) # Puede lanzar ValueError

        # Actualizar objeto
        movie.title = new_title
        movie.director = new_director
        movie.year = year
        movie.genre = new_genre

        db.session.commit()
        print(f"--- [DEBUG] Película ID {movie_id} actualizada en BD y commit realizado.")
        flash('Película actualizada correctamente.', 'success')
    except ValueError:
        flash('El año debe ser un número válido al actualizar.', 'warning')
        print(f"--- [ERROR] ValueError al actualizar año para ID {movie_id}.")
        # Volver a renderizar el formulario con los datos originales (o actuales antes del error)
        return render_template('edit_movie.html', movie=movie)
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la base de datos ({type(e).__name__})', 'danger')
        print(f"--- [ERROR] Error al actualizar BD para ID {movie_id}: {e}. Rollback realizado.")
        import traceback
        traceback.print_exc()
    return redirect(url_for('index'))


# Eliminar película de la BD (desde botón/formulario frontend)
@app.route('/collection/delete/<int:movie_id>', methods=['POST'])
def delete_movie_db(movie_id):
    print(f"--- [DEBUG] Recibida petición POST a /collection/delete/{movie_id} ---")
    movie = db.get_or_404(Movie, movie_id, description=f"No se encontró película con ID {movie_id} para eliminar")
    print(f"--- [DEBUG] Película encontrada para eliminar: {movie}")
    try:
        db.session.delete(movie)
        db.session.commit()
        print(f"--- [DEBUG] Película ID {movie_id} eliminada de BD y commit realizado.")
        flash('Película eliminada de tu colección.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar de la base de datos ({type(e).__name__})', 'danger')
        print(f"--- [ERROR] Error al eliminar de BD para ID {movie_id}: {e}. Rollback realizado.")
        import traceback
        traceback.print_exc()
    return redirect(url_for('index'))

# --- Contexto para comandos de Flask ---
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Movie': Movie}

if __name__ == '__main__':
    print("--- [INFO] Iniciando aplicación Flask ---")
    # Creamos las tablas si no existen DENTRO del contexto de la aplicación
    try:
        with app.app_context():
            print("--- [INFO] Entrando en app_context para db.create_all()... ---")
            db.create_all()
            print("--- [INFO] db.create_all() ejecutado (no hace nada si las tablas ya existen). ---")
    except Exception as e:
        print(f"--- [ERROR] Falló db.create_all(): {e} ---")

    print("--- [INFO] Iniciando servidor de desarrollo Flask... ---")
    app.run(debug=True, port=5005)