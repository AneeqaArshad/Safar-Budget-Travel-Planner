"""
Travel Planner - Main Flask Application
"""

from flask import Flask, render_template
from flask_cors import CORS

from flask_jwt_extended import JWTManager

from extensions import db, migrate

from config import Config

from routes.chat import chat_bp
from routes.itinerary import itinerary_bp
from routes.auth_routes import auth_bp

from services.data_loader import load_csv_data


def create_app(config_class=Config):

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    # ── Config ─────────────────────────────

    app.config.from_object(config_class)

    # ── JWT ────────────────────────────────

    jwt = JWTManager(app)

    # ── Extensions ─────────────────────────

    db.init_app(app)

    migrate.init_app(app, db)

    CORS(app)

    # ── Blueprints ─────────────────────────

    app.register_blueprint(
        chat_bp,
        url_prefix="/api/chat"
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        itinerary_bp,
        url_prefix="/api/itinerary"
    )

    # ── Frontend Routes ────────────────────

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/signup")
    def signup_page():
        return render_template("signup.html")

    # ── Startup Tasks ──────────────────────

    with app.app_context():

        load_csv_data()

        from services.place_retriever import collection

        if collection.count() == 0:

            from services.place_retriever import index_places

            index_places()
    @app.errorhandler(404)
    def not_found(error):

        return {
            "success": False,
            "message": "Resource not found"
        }, 404


    @app.errorhandler(500)
    def internal_error(error):

        return {
            "success": False,
            "message": "Internal server error"
        }, 500

    return app


# ── Run App ─────────────────────────────────

if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        use_reloader=False
    )