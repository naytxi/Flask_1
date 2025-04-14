# src/models.py
from flask_sqlalchemy import SQLAlchemy
import datetime  # Necesario para usar fechas por defecto

# Se crea la instancia de SQLAlchemy aquí, pero sin asociarla a ninguna app aún.
# Se inicializará en src/__init__.py con db.init_app(app)
db = SQLAlchemy()

class Movie(db.Model):
    # __tablename__ = 'movies' # Opcional: Especificar nombre de tabla explícito

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)

    # La relación inversa ('loans') se crea automáticamente gracias
    # al 'backref' en el modelo Loan. No necesitas definirla aquí explícitamente,
    # pero puedes hacerlo si quieres más control:
    # loans = db.relationship('Loan', backref='movie', lazy='dynamic') # 'dynamic' es otra opción de carga

    def to_dict(self):
        """Devuelve una representación del objeto Movie en diccionario."""
        return {
            'id': self.id,
            'title': self.title,
            'director': self.director,
            'year': self.year,
            'genre': self.genre,
            # Podrías añadir información relacionada si quisieras, e.g., número de préstamos activos
            # 'active_loans': Loan.query.with_parent(self).filter_by(returned=False).count()
        }

    def __repr__(self):
        """Representación en string del objeto para debugging."""
        return f'<Movie {self.id}: {self.title}>'


class Loan(db.Model):
    # __tablename__ = 'loans' # Opcional: Especificar nombre de tabla explícito

    id = db.Column(db.Integer, primary_key=True)
    # Clave foránea que apunta a la columna 'id' de la tabla 'movie'
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    borrower = db.Column(db.String(100), nullable=False)
    # Establecer la fecha actual como valor por defecto para loan_date
    loan_date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    # La fecha de devolución puede ser nula hasta que se devuelva
    return_date = db.Column(db.Date, nullable=True)
    # Estado del préstamo, por defecto no devuelto
    returned = db.Column(db.Boolean, default=False, nullable=False) # nullable=False es bueno aquí también

    # --- Definición de la Relación ---
    # Esto crea un atributo 'movie' en cada objeto Loan,
    # que te permite acceder al objeto Movie relacionado directamente (p. ej., loan.movie.title).
    # El 'backref' crea automáticamente un atributo 'loans' en cada objeto Movie,
    # permitiendo acceder a una lista (o query) de los préstamos asociados (p. ej., movie.loans).
    # 'lazy=True' (o 'select') es el comportamiento por defecto: carga la película relacionada
    # solo cuando accedes a `loan.movie`. Otras opciones son 'joined', 'subquery', 'dynamic'.
    movie = db.relationship('Movie', backref=db.backref('loans', lazy=True))
    # ---------------------------------

    def to_dict(self):
        """Devuelve una representación del objeto Loan en diccionario."""
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            # Puedes incluir info de la película relacionada fácilmente gracias a la relationship
            'movie_title': self.movie.title if self.movie else None,
            'borrower': self.borrower,
            'loan_date': self.loan_date.isoformat() if self.loan_date else None, # Formato ISO estándar para fechas
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'returned': self.returned,
        }

    def __repr__(self):
        """Representación en string del objeto para debugging."""
        # Accedemos al título de la película directamente a través de la relación
        movie_title = self.movie.title if self.movie else "ID: " + str(self.movie_id)
        return f'<Loan {self.id} for "{movie_title}" to {self.borrower}>'