from flask import Flask, app
from app.database import db
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    
    load_dotenv()
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
    
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)


    from .models import User, Bookmark
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp) 
    from .routes.bookmarks import bookmarks_bp
    app.register_blueprint(bookmarks_bp)
    with app.app_context():
        db.create_all()
    from .routes.stats import stats_bp
    app.register_blueprint(stats_bp)
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(bookmarks_bp)
    


    return app