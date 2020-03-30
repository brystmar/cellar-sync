from backend.global_logger import logger
from backend.models import Beer
from flask import request
from flask_restful import Resource
from pynamodb.exceptions import PynamoDBException
import json


class CellarApi(Resource):
    """Endpoint: /api/v1/cellar """
    def get(self) -> json:
        """Return all beers in the database."""
        logger.debug(f"Request: {request}")

        try:
            # Read from the database
            beers = Beer.scan()

            # Convert each record to a dictionary, compile into a list
            output = []
            for beer in beers:
                output.append(beer.to_dict())

            return {'message': 'Success', 'data': output}, 200

        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beers from the database."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def post(self) -> json:
        """Add a new beer to the database using the submitted JSON."""
        logger.debug(f"Request: {request}")

        # Ensure there's a body to accompany this request
        if not request.data:
            return {'message': 'Error', 'data': 'POST request must contain a body.'}, 400

        # Load the provided JSON
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data submitted: {data}")
        except json.JSONDecodeError as e:
            error_msg = f"Error attempting to decode the provided JSON."
            logger.debug(f"{error_msg},\n{request.data.__str__()},\n{e}")
            return {'message': 'Error', 'data': error_msg + f"\n{request.data.__str__()}"}, 400

        # Create a new Beer from the provided data

        return {}
