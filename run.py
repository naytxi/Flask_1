# run.py
import os
from src import create_app # Importa la factory desde el paquete src

# Determina qué configuración usar (p.ej., desde una variable de entorno)
# Si no se especifica, usa 'default' (que es DevelopmentConfig en nuestro caso)
config_name = os.getenv('FLASK_CONFIG') or 'development'

# Crea la instancia de la aplicación usando la factory
app = create_app(config_name)

# El bloque if __name__ == '__main__': permite ejecutar directamente con 'python run.py'
if __name__ == '__main__':
    print("--- [INFO] Iniciando servidor de desarrollo Flask desde run.py... ---")
    # Lee el puerto desde el entorno o usa 5005 por defecto
    port = int(os.environ.get("PORT", 5005))
    # debug=True se toma de la configuración (app.config['DEBUG'])
    # app.run(host='0.0.0.0', port=port) # Escuchar en todas las interfaces (útil para Docker)
    app.run(port=port) # debug=True ya está establecido por DevelopmentConfig