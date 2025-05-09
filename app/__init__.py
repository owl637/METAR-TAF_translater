from flask import Flask
import os

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
    app.secret_key = "your_secret_key"  # セッションのために必須（本番は安全な値を）
    
    from .routes import main
    app.register_blueprint(main)

    return app
