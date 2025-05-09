from flask import Flask
import os

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.secret_key = os.urandom(24)
    
    from .routes import main
    app.register_blueprint(main)

    return app
