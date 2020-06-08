from backend.global_logger import logger
from backend.models import Beverage
from flask import request
from flask_restful import Resource
from pynamodb.exceptions import PynamoDBException
from datetime import datetime
import json


class CellarCollectionApi(Resource):
    """
    For requesting the entire cellar inventory and submitting new beverages.
    Endpoint: /api/v1/cellar
    """
    def get(self) -> json:
        """Return all beverages in the database."""
        logger.debug(f"Request: {request}")

        try:
            # Read from the database
            beverages = Beverage.scan()

            # Convert each record to a dictionary, compile into a list
            output = []
            count = 0
            for bev in beverages:
                output.append(bev.to_dict(dates_as_epoch=True))
                count += 1

            logger.debug(f"End of CellarCollectionApi.GET")
            return {'message': 'Success', 'data': output}, 200

        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beverages from the database."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def post(self) -> json:
        """Add a new beverage to the database based on the provided JSON."""
        logger.debug(f"Request: {request}")

        # Ensure there's a body to accompany this request
        if not request.data:
            return {'message': 'Error', 'data': 'POST request must contain a body.'}, 400

        # Load the provided JSON
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data submitted: {type(data)}, {data}")
            # Replace empty strings with None
            for key in data.keys():
                if data[key] == "":
                    data[key] = None

            logger.debug(f"Data post-cleaning: {type(data)}, {data}")

        except json.JSONDecodeError as e:
            error_msg = f"Error attempting to decode the provided JSON."
            logger.debug(f"{error_msg},\n{request.data.__str__()},\n{e}")
            return {'message': 'Error', 'data': error_msg + f"\n{request.data.__str__()}"}, 400
        except BaseException as e:
            error_msg = f"Unknown error attempting to parse the provided JSON.\n{e}"
            logger.debug(error_msg)
            return {'message': 'Error', 'data': error_msg}, 400

        # Create a new Beverage from the provided data
        try:
            new_beverage = Beverage(**data)
            logger.debug(f"New Beverage created: {new_beverage}")

        except PynamoDBException as e:
            error_msg = f"Error attempting to create new Beverage from: {data}."
            logger.debug(f"{error_msg}\nError: {e}.")
            return {'message': 'Error', 'data': error_msg}, 500
        except BaseException as e:
            error_msg = f"Unknown error creating a new Beverage from: {data}."
            logger.debug(f"{error_msg}\n{e}.")
            return {'message': 'Error', 'data': error_msg}, 500

        # Write this Beverage to the database
        try:
            logger.debug(f"Attempting to save Beverage {new_beverage} to the database.")
            new_beverage.save()
            logger.info(f"Successfully saved {new_beverage}.")
            logger.debug(f"End of CellarCollectionApi.POST")

            return {'message': 'Created', 'data': new_beverage.to_dict(dates_as_epoch=True)}, 201
        except PynamoDBException as e:
            error_msg = f"Error attempting to save new beverage."
            logger.debug(f"{error_msg}\n{new_beverage}: {e}.")
            return {'message': 'Error', 'data': error_msg}, 500


class BeverageApi(Resource):
    """
    For requesting, updating, or deleting a single beverage from the database.
    Endpoint: /api/v1/cellar/<beverage_id>/<location>
    """
    def get(self, beverage_id, location) -> json:
        """Return the specified beverage."""
        logger.debug(f"Request: {request}, for id: {beverage_id}, loc: {location}.")

        # Retrieve specified beverage from the database
        try:
            beverage = Beverage.get(beverage_id, location)
            logger.debug(f"Retrieved beverage: {beverage}")
            return {'message': 'Success', 'data': beverage.to_dict(dates_as_epoch=True)}, 200

        except Beverage.DoesNotExist:
            logger.debug(f"Beverage {beverage_id} not found.")
            return {'message': 'Not Found', 'data': f'Beverage {beverage_id} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beverage {beverage_id}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def put(self, beverage_id, location) -> json:
        """Update the specified beverage."""
        logger.debug(f"Request: {request}, for id: {beverage_id}, loc: {location}.")

        # Ensure there's a body to accompany this request
        if not request.data:
            return {'message': 'Error', 'data': 'PUT request must contain a body.'}, 400

        # Load & decode the provided JSON
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data submitted: {data}")

        except json.JSONDecodeError as e:
            error_msg = f"Error attempting to decode the provided JSON."
            logger.debug(f"{error_msg},\n{request.data.__str__()},\n{e}")
            return {'message': 'Error', 'data': error_msg + f"\n{request.data.__str__()}"}, 400
        except BaseException as e:
            error_msg = f"Unknown error attempting to parse the provided JSON.\n{e}"
            logger.debug(error_msg)
            return {'message': 'Error', 'data': error_msg}, 400

        # Ensure the variables provided to the endpoint match the body details.
        if str(beverage_id) != str(data['beverage_id']):
            error_msg = f"/beverage_id provided to the endpoint ({beverage_id}) " \
                        f"doesn't match the beverage_id from the body ({data['beverage_id']})."
            logger.debug(f"{error_msg}")
            return {'message': 'Error', 'data': error_msg}, 400
        elif str(location) != str(data['location']):
            error_msg = f"/location provided to the endpoint ({location}) " \
                        f"doesn't match the location from the body ({data['location']})."
            logger.debug(f"{error_msg}")
            return {'message': 'Error', 'data': error_msg}, 400

        # Create a Beverage instance from the provided data
        try:
            beverage = Beverage(**data)
            beverage.last_modified = datetime.utcnow()
            logger.debug(f"Beverage instance created: {beverage}")

        except PynamoDBException as e:
            error_msg = f"Error parsing data into the Beverage model."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': f'{error_msg}\n{e}'}, 500

        # Save to the database
        try:
            logger.debug(f"Saving {beverage} to the db...")
            beverage.save()
            logger.info(f"Beverage updated: {beverage})")
            logger.debug(f"End of BeverageApi.PUT")
            return {'message': 'Success', 'data': beverage.to_dict(dates_as_epoch=True)}, 200
        except Beverage.DoesNotExist:
            logger.debug(f"Beverage {beverage_id} not found.")
            return {'message': 'Not Found', 'data': f'Beverage {beverage_id} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to save beverage {beverage_id}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def delete(self, beverage_id, location) -> json:
        """Delete the specified beverage."""
        logger.debug(f"Request: {request}, for id: {beverage_id}, loc: {location}.")

        # Retrieve this beverage from the database
        try:
            beverage = Beverage.get(beverage_id, location)
            logger.debug(f"Retrieved beverage: {beverage}")

        except Beverage.DoesNotExist:
            logger.debug(f"Beverage {beverage_id} not found.")
            return {'message': 'Not Found', 'data': f'Beverage {beverage_id} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beverage {beverage_id}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

        # Delete the specified beverage
        try:
            footprint = f"{beverage}"
            beverage.delete()
            logger.info(f"Beverage {footprint} deleted successfully.")
            logger.debug("End of BeverageApi.DELETE")
            return {'message': 'Success', 'data': f'{footprint} deleted successfully.'}, 200

        except PynamoDBException as e:
            error_msg = f"Error attempting to delete beverage: {beverage}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500
