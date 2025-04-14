# src/routes/main_routes.py
from flask import (Blueprint, render_template, request, flash,
                   redirect, url_for, current_app, abort)
import requests
# Importamos 'db' y 'Movie' desde el módulo de modelos en el mismo paquete (src)
from ..models import db, Movie
import traceback # Para imprimir errores detallados

# Creamos un Blueprint para las rutas principales/frontend.
main_bp = Blueprint('main', __name__)

# --- Rutas NUEVAS (Para Frontend, usan movies.db real) ---

@main_bp.route('/')
def index():
    print("--- [DEBUG] Entrando a la ruta '/' ---")
    # Accedemos a la configuración a través de current_app
    api_key = current_app.config['API_KEY']
    base_url = current_app.config['BASE_URL']
    image_base_url = current_app.config['IMAGE_BASE_URL']

    # Datos para el Carrusel (desde API externa)
    peliculas_api_carousel = []
    try:
        response = requests.get(f'{base_url}movie/popular', params={'api_key': api_key, 'language': 'es-ES'}, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        max_items_deseados = 12
        num_items_api = len(results)
        num_a_tomar = min(max_items_deseados, num_items_api)
        peliculas_api_carousel = results[:num_a_tomar]
        for pelicula in peliculas_api_carousel:
            poster_path = pelicula.get('poster_path')
            pelicula['poster_url'] = f'{image_base_url}{poster_path}' if poster_path else url_for('static', filename='images/default_poster.png')
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
        # Usamos el modelo importado
        lista_peliculas_db = Movie.query.order_by(Movie.title).all()
        print(f"--- [DEBUG] {len(lista_peliculas_db)} películas obtenidas de la base de datos local.")
    except Exception as e:
        flash(f'Error al leer la colección local: ({type(e).__name__})', 'danger')
        print(f"--- [ERROR] Falló la consulta a la base de datos: {e} ---")
        traceback.print_exc()

    print("--- [DEBUG] Renderizando plantilla index.html... ---")
    return render_template('index.html',
                           peliculas_api=peliculas_api_carousel,
                           peliculas_db=lista_peliculas_db)

# Añadir película a la BD (desde formulario frontend)
@main_bp.route('/collection/add', methods=['POST'])
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
            # Usamos el modelo importado
            nueva_pelicula = Movie(title=title, director=director, year=year, genre=genre)
            print(f"--- [DEBUG] Creando objeto Movie: {nueva_pelicula}")
            db.session.add(nueva_pelicula) # Usamos db importado
            db.session.commit()
            print("--- [DEBUG] Película añadida a la BD y commit realizado.")
            flash('Película añadida a tu colección.', 'success')
        except ValueError:
            flash('El año debe ser un número válido.', 'warning')
            print("--- [ERROR] Error de ValueError al convertir año.")
        except Exception as e:
            db.session.rollback() # Importante hacer rollback en caso de error
            flash(f'Error al guardar en la base de datos ({type(e).__name__})', 'danger')
            print(f"--- [ERROR] Error al guardar en BD: {e}. Rollback realizado.")
            traceback.print_exc()
    return redirect(url_for('main.index')) # Referencia a la ruta del blueprint: blueprint_name.function_name

# Mostrar formulario para editar película de la BD
@main_bp.route('/collection/edit/<int:movie_id>', methods=['GET'])
def edit_movie_db_form(movie_id):
    print(f"--- [DEBUG] Recibida petición GET a /collection/edit/{movie_id} ---")
    # Usamos db.get_or_404 que es más conciso
    movie = db.get_or_404(Movie, movie_id, description=f"No se encontró película con ID {movie_id}")
    print(f"--- [DEBUG] Película encontrada para editar: {movie}")
    return render_template('edit_movie.html', movie=movie)


# Actualizar película en la BD (desde formulario de edición)
@main_bp.route('/collection/update/<int:movie_id>', methods=['POST'])
def update_movie_db(movie_id):
    print(f"--- [DEBUG] Recibida petición POST a /collection/update/{movie_id} ---")
    movie = db.get_or_404(Movie, movie_id, description=f"No se encontró película con ID {movie_id} para actualizar")
    print(f"--- [DEBUG] Película encontrada para actualizar: {movie}")

    try:
        new_title = request.form.get('title')
        new_director = request.form.get('director')
        new_year_str = request.form.get('year')
        new_genre = request.form.get('genre')
        print(f"--- [DEBUG] Datos recibidos para actualizar: Title={new_title}, Director={new_director}, Year={new_year_str}, Genre={new_genre}")

        # Validar y actualizar
        if not all([new_title, new_director, new_year_str, new_genre]):
             flash('Todos los campos son obligatorios al actualizar.', 'warning')
             # Volver a renderizar el formulario con los datos actuales para que el usuario corrija
             return render_template('edit_movie.html', movie=movie)

        year = int(new_year_str) # Puede lanzar ValueError

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
        # Importante renderizar de nuevo la plantilla de edición en caso de error de validación
        return render_template('edit_movie.html', movie=movie) # Muestra el error en el mismo formulario
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la base de datos ({type(e).__name__})', 'danger')
        print(f"--- [ERROR] Error al actualizar BD para ID {movie_id}: {e}. Rollback realizado.")
        traceback.print_exc()
        # En caso de error de BD, redirigir a index puede ser mejor que mostrar el form de nuevo
        return redirect(url_for('main.index'))

    return redirect(url_for('main.index'))


# Eliminar película de la BD (desde botón/formulario frontend)
# Usamos POST para la eliminación por buenas prácticas (GET no debería cambiar estado)
@main_bp.route('/collection/delete/<int:movie_id>', methods=['POST'])
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
        traceback.print_exc()
    return redirect(url_for('main.index')) # Siempre redirigir después de POST exitoso o fallido (patrón PRG)