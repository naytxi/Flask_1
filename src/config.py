# src/config.py
import os

# Determina la ruta base del proyecto (un nivel arriba de 'src')
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# OJO: Flask maneja la ruta 'instance' de forma más directa si usamos instance_relative_config=True

class Config:
    """Clase base de configuración."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mi_clave_secreta_super_segura_123!' # Mejor usar variables de entorno en producción
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # No definimos SQLALCHEMY_DATABASE_URI aquí porque depende de app.instance_path

    # Claves y URLs API (pueden ir aquí o cargarse desde entorno)
    API_KEY = os.environ.get('TMDB_API_KEY') or '0793a5c442c049e9b0321cf71326063b' # Mejor usar variables de entorno
    BASE_URL = 'https://api.themoviedb.org/3/'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w342'

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    # La URI de la BD se establecerá en create_app usando app.instance_path

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    # En producción, podrías usar PostgreSQL, MySQL, etc.
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@host:port/database'

# Podrías tener otras como TestingConfig, etc.

# Un diccionario para seleccionar la configuración fácilmente
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}