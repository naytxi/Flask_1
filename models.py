# Aquí estamos creando una clase llamada Movie. Una clase es como un molde o plantilla para crear objetos
class Movie:
    def __init__(self, title, year, genre, plot): # Funcion constructor que se ejecuta automaticamente cada vez que creamos un nuevo objeto movie
        self.id = id(self)  
        self.title = title
        self.year = year
        self.genre = genre
        self.plot = plot
    # Esta función convierte el objeto de tipo Movie a un diccionario de Python.
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            'plot': self.plot
        }