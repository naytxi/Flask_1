from flask_sqlalchemy import SQLAlchemy

# Creamos una instancia de SQLAlchemy aquí, que importaremos en app.py
# Esto ayuda a evitar importaciones circulares.
db = SQLAlchemy()

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'director': self.director,
            'year': self.year,
            'genre': self.genre,
        }

    def __repr__(self):
        return f'<Movie {self.title}>'