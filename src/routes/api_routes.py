# src/routes/api_routes.py
from flask import Blueprint, request, jsonify, current_app # Mantenemos current_app por si se usa logger o algo más
import requests
import logging # Importamos logging para registrar errores

# --- Constantes definidas a nivel de módulo ---
# Estas constantes SÓLO estarán disponibles para las funciones en ESTE archivo.
API_KEY = '0793a5c442c049e9b0321cf71326063b'
BASE_URL = 'https://api.themoviedb.org/3/'
# IMAGE_BASE_URL no se usa en estas rutas de API, pero la dejamos si quieres
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w342'
# ---------------------------------------------

# Creamos un Blueprint para estas rutas. 'api' es el nombre del blueprint.
# url_prefix='/api' hará que todas las rutas aquí definidas empiecen con /api
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Mantenemos la 'base de datos' en memoria para estas rutas específicas
movies_db_memory = []

# --- Rutas ORIGINALES (Para Postman, usan API externa y movies_db_memory) ---

@api_bp.route('/movies', methods=['POST'])
def add_movie_api():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'El título es obligatorio'}), 400

    # --- Usamos las constantes definidas arriba en este módulo ---
    try:
        # Usamos directamente las variables API_KEY y BASE_URL definidas en este archivo
        response = requests.get(
            f'{BASE_URL}search/movie', # Usa la constante BASE_URL del módulo
            params={'query': title, 'api_key': API_KEY, 'language': 'es-ES'}, # Usa la constante API_KEY del módulo
            timeout=10
        )
        response.raise_for_status()  # Verifica si hubo errores HTTP (4xx o 5xx)

    except requests.exceptions.RequestException as e:
        # Es buena idea registrar el error real para depuración
        logging.error(f"Error API externa en add_movie_api: {e}")
        # Devolver un error genérico al cliente
        return jsonify({'error': f'Error al conectar con la API externa'}), 500
    # --- Fin Modificación ---

    data = response.json()
    if data.get('results'):
        movie_data = data['results'][0]
        movie = {
            'id': len(movies_db_memory) + 1,
            'title': movie_data.get('title', 'N/A'),
            'year': movie_data.get('release_date', 'N/A')[:4] if movie_data.get('release_date') else 'N/A',
            'genre': 'N/A',
            'plot': movie_data.get('overview', 'N/A')
        }
        movies_db_memory.append(movie)
        return jsonify(movie), 201
    else:
        return jsonify({'error': 'Pelicula no encontrada en API externa'}), 404

# --- Las otras rutas (GET, PUT, DELETE para la API en memoria) no necesitan las constantes ---

@api_bp.route('/movies', methods=['GET'])
def get_movies_api():
    return jsonify(movies_db_memory)

@api_bp.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_api(movie_id):
    movie = next((m for m in movies_db_memory if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Pelicula no encontrada en memoria'}), 404
    return jsonify(movie)

@api_bp.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie_api(movie_id):
    movie = next((m for m in movies_db_memory if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Pelicula no encontrada en memoria'}), 404
    data = request.json
    movie['title'] = data.get('title', movie['title'])
    movie['year'] = data.get('year', movie['year'])
    movie['genre'] = data.get('genre', movie['genre'])
    movie['plot'] = data.get('plot', movie['plot'])
    return jsonify(movie)

@api_bp.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie_api(movie_id):
    global movies_db_memory
    initial_len = len(movies_db_memory)
    movies_db_memory = [m for m in movies_db_memory if m['id'] != movie_id]
    if len(movies_db_memory) == initial_len:
        return jsonify({'error': 'Pelicula no encontrada en memoria'}), 404
    return jsonify({'message': 'Pelicula eliminada de memoria'}), 200