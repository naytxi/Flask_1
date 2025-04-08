
from flask import Flask, jsonify, request # Marco de framework de flask, devolver respuestas en formato Json.
 # type: ignore
from flask import Flask, render_template, request, jsonify # Marco de framework de flask, devolver respuestas en formato Json.
import requests # Acceder a las llamadas a la API
import random # Eleccion aleatoria de caratulas de peliculas

app = Flask(__name__) # Orden a flask de iniciar la app

# Clave de la api y direccion base de la url
API_KEY = '0793a5c442c049e9b0321cf71326063b'
BASE_URL = 'https://api.themoviedb.org/3/'

IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w342'

# Base de datos en memoria para almacenar las películas, la usamos solo mientras la app esta en ejecucion
movies_db = []
import random
import requests
from flask import Flask, render_template

app = Flask(__name__)

API_KEY = '0793a5c442c049e9b0321cf71326063b'
BASE_URL = 'https://api.themoviedb.org/3/'

IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w342'

# Base de datos en memoria para almacenar las películas, la usamos solo mientras la app esta en ejecucion
movies_db = []

@app.route('/')
def index():
    # Realizar una solicitud a la API para obtener películas populares
    response = requests.get(f'{BASE_URL}movie/popular', params={'api_key': API_KEY})
    if response.status_code == 200:
        data = response.json()
        peliculas = data.get('results', [])
        # Seleccionar un número determinado de películas aleatorias
        peliculas_aleatorias = random.sample(peliculas, min(5, len(peliculas)))
        # Construir las URLs completas de las imágenes
        for pelicula in peliculas_aleatorias:
            poster_path = pelicula.get('poster_path')
            if poster_path:
                pelicula['poster_url'] = f'{IMAGE_BASE_URL}{poster_path}'
        return render_template('index.html', peliculas=peliculas_aleatorias)
    else:
        return 'Error al obtener datos de la API', 500

# Crear (Añadir una película a la base de datos)
@app.route('/movies', methods=['POST'])
def add_movie():
    title = request.json.get('title') # Cogemos el titulo de el cuerpo de la solicitud
    if not title:
        return jsonify({'error': 'El título es obligatorio'}), 400

    # Buscar la película en API externa, mandamos titulo y clave para la busqueda (TMDb)
    response = requests.get(f'{BASE_URL}search/movie', params={'query': title, 'api_key': API_KEY})

    if response.status_code != 200: # Verificamos respuesta de la API
        return jsonify({'error': 'Error al conectar con la API externa'}), 500

    # Convertir la respuesta en formato JSON
    data = response.json()

    # Verificar si se encontraron resultados y si es asi se coge la primera aparicion
    if data.get('results'):
        movie_data = data['results'][0]  
        movie = { # Creacion de diccionario 
            'id': len(movies_db) + 1,  # Asigna un ID único (se ba sumando)
            'title': movie_data['title'],
            'year': movie_data['release_date'][:4],  #
            'genre': 'N/A', 
            'plot': movie_data['overview']
        }
        movies_db.append(movie) # Se agrega a la base de datos antes declarada
        return jsonify(movie), 201
    else:
        return jsonify({'error': 'Pelicula no encontrada'}), 404 # Si no es asi mostramos el error

# Leer todas las películas de tu base de datos local
@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies_db)

# Leer una película por ID
@app.route('/movies/<int:movie_id>', methods=['GET']) # Se ejecuta cuando hacemos solicitud con el id de la peli
def get_movie(movie_id):
    movie = next((m for m in movies_db if m['id'] == movie_id), None) # Se busca en la base de datos local
    if not movie:
        return jsonify({'error': 'Pelicula no encontrada'}), 404
    return jsonify(movie)

# Actualizar una película por ID
@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    movie = next((m for m in movies_db if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Pelicula no encontrada'}), 404

    # Obtener los nuevos datos de la película
    data = request.json
    movie['title'] = data.get('title', movie['title']) # Si el dato esta lo actualizamos, sino dejamos el actual
    movie['year'] = data.get('year', movie['year'])
    movie['genre'] = data.get('genre', movie['genre'])
    movie['plot'] = data.get('plot', movie['plot'])

    return jsonify(movie)

# Editar una película por ID
@app.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    movie = next((m for m in movies_db if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Película no encontrada'}), 404

# Eliminar una película por ID
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    global movies_db # Ncesitamos usar global ya que es una variable global, si quiero modificar debo poner eso
    movie = next((m for m in movies_db if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Pelicula no encontrada'}), 404

    # Eliminar la película de  base de datos
    movies_db = [m for m in movies_db if m['id'] != movie_id]
    return jsonify({'message': 'Pelicula eliminada'}), 200

if __name__ == '__main__':
    app.run(debug=True,port=5005)
