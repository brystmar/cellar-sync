from backend.global_logger import logger
from backend.models import Picklist
from flask import request
from flask_restful import Resource
from pynamodb.exceptions import PynamoDBException
from datetime import datetime
import json


class PicklistApi(Resource):
    """
    Handles the pre-defined values for picklist fields:
      `location`, `size`, `style`
    Endpoint: /api/v1/picklist-data
    """
    def get(self) -> json:
        """Return the list of picklist values for all fields."""
        logger.debug(f"Request: {request}")

        try:
            # Read from the database
            logger.debug("Retrieving all picklist values...")
            all_picklists = Picklist.scan()

            # Convert each record to a dictionary, compile into a list
            output = []
            for picklist in all_picklists:
                output.append(picklist.to_dict())
                # picklist.save()
                # output = picklist.to_dict()
                # pass

            logger.debug(f"End of PicklistApi.GET")
            return {'message': 'Success', 'data': output}, 200

        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve picklists from the database."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def put(self) -> json:
        """Add/update the list of picklist values."""
        logger.debug(f"Request: {request}")

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

        # Create a Picklist instance from the provided data
        try:
            picklist = Picklist(**data)
            picklist.last_modified = datetime.utcnow()
            logger.debug(f"Picklist instance created: {picklist}")

        except PynamoDBException as e:
            error_msg = f"Error parsing data into the Picklist model."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': f'{error_msg}\n{e}'}, 500

        # Save to the database
        try:
            logger.debug(f"Saving {picklist} to the db...")
            picklist.save()
            logger.info(f"Picklist updated: {picklist.list_name})")
            logger.debug(f"End of PicklistApi.PUT")
            return {'message': 'Success', 'data': picklist.to_dict()}, 200
        except Picklist.DoesNotExist:
            logger.debug(f"Picklist {picklist} not found.")
            return {'message': 'Not Found', 'data': f'Picklist {picklist} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to save picklist {picklist}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500
