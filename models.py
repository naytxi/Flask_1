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

#creamos una segunda tabla relacionada directamente con la primera con la foreignkey y movies.id
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    borrower = db.Column(db.String(100), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    returned = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'borrower': self.borrower,
            'loan_date': self.loan_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'returned': self.returned,
        }

    def __repr__(self):
        return f'<Loan {self.borrower} - {self.movie.title}>'