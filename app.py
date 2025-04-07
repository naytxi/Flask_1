from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# clave de la api y direccion base de la url
API_KEY = '0793a5c442c049e9b0321cf71326063b'
BASE_URL = 'https://api.themoviedb.org/3/'

# Base de datos en memoria para almacenar las películas
movies_db = []

# Crear (Añadir una película a la base de datos)
@app.route('/movies', methods=['POST'])
def add_movie():
    title = request.json.get('title')
    if not title:
        return jsonify({'error': 'El título es obligatorio'}), 400

    # Buscar la película en API externa (TMDb)
    response = requests.get(f'{BASE_URL}search/movie', params={'query': title, 'api_key': API_KEY})

    if response.status_code != 200:
        return jsonify({'error': 'Error al conectar con la API externa'}), 500

    # Convertir la respuesta en formato JSON
    data = response.json()

    # Verificar si se encontraron resultados
    if data.get('results'):
        movie_data = data['results'][0]  # Coger el primer resultado
        movie = {
            'id': len(movies_db) + 1,  # Asigna un ID único (se ba sumando)
            'title': movie_data['title'],
            'year': movie_data['release_date'][:4],  #
            'genre': 'N/A', 
            'plot': movie_data['overview']
        }
        movies_db.append(movie)
        return jsonify(movie), 201
    else:
        return jsonify({'error': 'Pelicula no encontrada'}), 404

# Leer todas las películas de tu base de datos local
@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies_db)

# Leer una película por ID
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = next((m for m in movies_db if m['id'] == movie_id), None)
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
    movie['title'] = data.get('title', movie['title'])
    movie['year'] = data.get('year', movie['year'])
    movie['genre'] = data.get('genre', movie['genre'])
    movie['plot'] = data.get('plot', movie['plot'])

    return jsonify(movie)

# Eliminar una película por ID
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    global movies_db
    movie = next((m for m in movies_db if m['id'] == movie_id), None)
    if not movie:
        return jsonify({'error': 'Pelicula no encontrada'}), 404

    # Eliminar la película de  base de datos
    movies_db = [m for m in movies_db if m['id'] != movie_id]
    return jsonify({'message': 'Pelicula eliminada'}), 200

if __name__ == '__main__':
    app.run(debug=True)
