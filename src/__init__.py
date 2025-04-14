# src/__init__.py
import os
import traceback # Para imprimir errores detallados
from flask import Flask

# Importamos la instancia db y los modelos desde models.py (usando import relativo)
from .models import db, Movie, Loan
# Importamos el diccionario de configuraciones desde config.py (usando import relativo)
from .config import config_by_name

def create_app(config_name='default'):
    """
    Application Factory Function: Crea y configura la instancia de la aplicación Flask.

    Args:
        config_name (str): El nombre de la configuración a usar ('development', 'production', etc.).

    Returns:
        Flask: La instancia de la aplicación Flask configurada.
    """
    print(f"--- [INFO] Creando aplicación Flask con config '{config_name}' ---")

    # Usamos instance_relative_config=True para que Flask busque la carpeta 'instance'
    # relativa al directorio raíz de la aplicación (donde está 'run.py', un nivel arriba de 'src').
    # Especificamos explícitamente las carpetas de plantillas y estáticos relativas a 'src'.
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder='templates',
                static_folder='static')

    # Cargar la configuración desde el objeto correspondiente en config.py
    try:
        config_object = config_by_name[config_name]
        app.config.from_object(config_object)
        print(f"--- [INFO] Configuración '{config_name}' cargada: DEBUG={app.config.get('DEBUG')} ---")
    except KeyError:
        print(f"--- [ERROR] Configuración '{config_name}' no encontrada. Usando 'default'. ---")
        config_name = 'default'
        app.config.from_object(config_by_name[config_name])

    # --- Configuración específica de la Base de Datos ---
    # Asegurarse de que la carpeta 'instance' existe (Flask la busca relativa al root del proyecto)
    try:
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
            print(f"--- [INFO] Carpeta 'instance' creada en: {app.instance_path} ---")
        else:
             print(f"--- [INFO] Carpeta 'instance' ya existe en: {app.instance_path} ---")
    except OSError as e:
        print(f"--- [ERROR] No se pudo crear la carpeta 'instance': {e} ---")
        # Considera lanzar una excepción si la carpeta es crucial y no se puede crear

    # Construir la ruta completa a la BD DENTRO de la carpeta instance
    db_filename = 'movies.db' # Nombre del archivo de la base de datos
    db_path = os.path.join(app.instance_path, db_filename)

    # Establecer la URI de la base de datos en la configuración de Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    print(f"--- [INFO] Configurando SQLAlchemy ---")
    print(f"--- [INFO] Usando DB en: {app.config['SQLALCHEMY_DATABASE_URI']} ---")
    print(f"--- [INFO] ¿Existe el archivo DB '{db_filename}'? {os.path.exists(db_path)} ---")
    # --------------------------------------------------

    # Inicializar extensiones (SQLAlchemy en este caso) con la app
    try:
        db.init_app(app) # Ahora asociamos la instancia 'db' con nuestra 'app'
        print("--- [INFO] SQLAlchemy inicializado con la app. ---")
    except Exception as e:
        print(f"--- [ERROR] Falló db.init_app(app): {e} ---")
        # Podrías querer detener la creación de la app aquí si la BD es esencial

    # --- Registrar Blueprints ---
    # Importar los blueprints DENTRO de la función para evitar problemas de importación circular
    try:
        from .routes.main_routes import main_bp
        app.register_blueprint(main_bp)
        print("--- [INFO] Blueprint 'main' registrado. ---")

        from .routes.api_routes import api_bp
        # Registramos el blueprint de la API con su prefijo URL
        app.register_blueprint(api_bp, url_prefix='/api')
        print(f"--- [INFO] Blueprint 'api' registrado con prefijo '/api'. ---")
    except ImportError as e:
         print(f"--- [ERROR] Falló la importación o registro de Blueprints: {e} ---")
         # Podrías querer detener la creación de la app aquí

    # --- Contexto para comandos de Flask y Shell ---
    @app.shell_context_processor
    def make_shell_context():
        """
        Hace que 'db', 'Movie' y 'Loan' estén disponibles
        automáticamente en el comando 'flask shell'.
        """
        return {'db': db, 'Movie': Movie, 'Loan': Loan}

    # --- Comandos CLI personalizados ---
    @app.cli.command('init-db')
    def init_db_command():
        """Comando para crear/inicializar las tablas de la base de datos."""
        try:
            # Es crucial ejecutar create_all dentro del contexto de la aplicación
            with app.app_context():
                 print("--- [INFO] Ejecutando db.create_all() dentro de app_context... ---")
                 db.create_all()
                 print("--- [INFO] db.create_all() completado (tablas creadas si no existían). ---")
                 print(f"--- [INFO] Base de datos debería estar lista en: {app.config['SQLALCHEMY_DATABASE_URI']} ---")
        except Exception as e:
            print(f"--- [ERROR] Falló el comando init-db: {e} ---")
            traceback.print_exc() # Imprime el stack trace completo del error

    # --- Finalización ---
    print("--- [INFO] Creación de la aplicación Flask completada. ---")
    return app