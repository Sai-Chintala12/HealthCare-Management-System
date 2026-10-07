import os
from flask import Flask
from .extensions import db, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60  # 1 hour

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    from .routes.auth import auth_bp
    from .routes.health import health_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(health_bp, url_prefix="/api/health")

    @app.get("/api/ping")
    def ping():
        return {"status": "ok"}

    with app.app_context():
        db.create_all()  # replace with migrations (Flask-Migrate) later

    return app