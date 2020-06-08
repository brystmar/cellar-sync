# Logging & config
from backend.global_logger import logger
from backend.config import Config

# External packages
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

# App components
from backend.cellar_routes import CellarCollectionApi, BeverageApi
from backend.picklist_routes import PicklistApi

app = Flask("cellar-sync-backend")
logger.info(f"Flask app {app.name} created!")

app.config.from_object(Config)
logger.info("Applied config parameters to the app.")

# Enable CORS for the app to ensure our UI can call the backend API
#   See: https://flask-cors.readthedocs.io/en/latest/
CORS(app, resources={r"/api/*": {"origins": Config.WHITELISTED_ORIGINS}})

api = Api(app)
logger.info("Flask-RESTful API initialized.")

# Define the functional endpoints
api.add_resource(CellarCollectionApi, '/api/v1/cellar')
api.add_resource(BeverageApi, '/api/v1/cellar/<beverage_id>/<location>')
api.add_resource(PicklistApi, '/api/v1/picklist-data')
