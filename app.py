from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # config is in project root
    app.config.from_pyfile('../config.py')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth_bp.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from auth.routes_auth import auth_bp
    app.register_blueprint(auth_bp)

    from docs.routes_docs import docs_bp
    app.register_blueprint(docs_bp)

    from rag.routes_rag import rag_bp
    app.register_blueprint(rag_bp)

    from quiz import quiz_bp
    app.register_blueprint(quiz_bp)

    @app.route('/')
    def home():
        if not current_user.is_authenticated:
            return redirect(url_for('auth_bp.login'))
        return redirect(url_for('docs_bp.upload'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
