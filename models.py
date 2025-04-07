class Movie:
    def __init__(self, title, year, genre, plot):
        self.id = id(self)  
        self.title = title
        self.year = year
        self.genre = genre
        self.plot = plot

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            'plot': self.plot
        }