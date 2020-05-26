from backend.global_logger import logger
from backend.models import Beer
from flask import request
from flask_restful import Resource
from pynamodb.exceptions import PynamoDBException
from datetime import datetime
import json


class CellarCollectionApi(Resource):
    """
    For requesting the entire cellar inventory and submitting brand new beers.
    Endpoint: /api/v1/cellar
    """
    def get(self) -> json:
        """Return all beers in the database."""
        logger.debug(f"Request: {request}")

        try:
            # Read from the database
            logger.debug("Here goes nothing...")
            beers = Beer.scan()

            # Convert each record to a dictionary, compile into a list
            output = []
            sizes = []
            locations = []
            styles = []
            specific_styles = []
            for beer in beers:
                # print(f"Saving beer #{count}: {beer}")
                output.append(beer.to_dict(dates_as_epoch=True))
                if beer.size not in sizes:
                    sizes.append(beer.size)
                if beer.location not in locations:
                    locations.append(beer.location)
                if beer.style not in styles:
                    styles.append(beer.style)
                if beer.specific_style not in specific_styles:
                    specific_styles.append(beer.specific_style)

            logger.debug(f"All beer sizes: {sizes}")
            logger.debug(f"All beer locations: {locations}")
            logger.debug(f"All beer styles: {styles}")
            logger.debug(f"All beer specific_styles: {specific_styles}")
            logger.debug(f"End of CellarCollectionApi.GET")
            return {'message': 'Success', 'data': output}, 200

        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beers from the database."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def post(self) -> json:
        """Add a new beer to the database based on the provided JSON."""
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
        except BaseException as e:
            error_msg = f"Unknown error attempting to parse the provided JSON.\n{e}"
            logger.debug(error_msg)
            return {'message': 'Error', 'data': error_msg}, 400

        # Create a new Beer from the provided data
        try:
            new_beer = Beer(**data)
            logger.debug(f"New Beer created: {new_beer}")

        except PynamoDBException as e:
            error_msg = f"Error attempting to create new Beer from: {data}."
            logger.debug(f"{error_msg}\nError: {e}.")
            return {'message': 'Error', 'data': error_msg}, 500
        except BaseException as e:
            error_msg = f"Unknown error creating a new Beer from: {data}."
            logger.debug(f"{error_msg}\n{e}.")
            return {'message': 'Error', 'data': error_msg}, 500

        # Write this Beer to the database
        try:
            logger.debug(f"Attempting to save Beer {new_beer} to the database.")
            new_beer.save()
            logger.info(f"Successfully saved {new_beer}.")
            logger.debug(f"End of CellarCollectionApi.POST")

            return {'message': 'Created', 'data': new_beer.to_dict(dates_as_epoch=True)}, 201
        except PynamoDBException as e:
            error_msg = f"Error attempting to save new beer."
            logger.debug(f"{error_msg}\n{new_beer}: {e}.")
            return {'message': 'Error', 'data': error_msg}, 500


class BeerApi(Resource):
    """
    For requesting, updating, or deleting a single beer from the database.
    Endpoint: /api/v1/cellar/<beer_id>
    """
    def get(self, beer_id) -> json:
        """Return the specified beer."""
        logger.debug(f"Request: {request}, for id: {beer_id}.")

        # Retrieve specified beer from the database
        try:
            beer = Beer.get(beer_id)
            logger.debug(f"Retrieved beer: {beer}")
            return {'message': 'Success', 'data': beer.to_dict(dates_as_epoch=True)}, 200

        except Beer.DoesNotExist:
            logger.debug(f"Beer {beer_id} not found.")
            return {'message': 'Not Found', 'data': f'Beer {beer_id} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beer {beer_id}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def put(self, beer_id) -> json:
        """Update the specified beer."""
        logger.debug(f"Request: {request}, for id: {beer_id}.")

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

        # Ensure the /<beer_id> provided to the endpoint matches the beer_id in the body.
        if str(beer_id) != str(data['beer_id']):
            error_msg = f"/beer_id provided to the endpoint ({beer_id}) " \
                        f"doesn't match the beer_id from the body ({data['beer_id']})."
            logger.debug(f"{error_msg}")
            return {'message': 'Error', 'data': error_msg}, 400

        # Create a Beer instance from the provided data
        try:
            beer = Beer(**data)
            beer.last_modified = datetime.utcnow()
            logger.debug(f"Beer instance created: {beer}")

        except PynamoDBException as e:
            error_msg = f"Error parsing data into the Beer model."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': f'{error_msg}\n{e}'}, 500

        # Save to the database
        try:
            logger.debug(f"Saving {beer} to the db...")
            beer.save()
            logger.info(f"Beer updated: {beer})")
            logger.debug(f"End of BeerApi.PUT")
            return {'message': 'Success', 'data': beer.to_dict(dates_as_epoch=True)}, 200
        except Beer.DoesNotExist:
            logger.debug(f"Beer {beer_id} not found.")
            return {'message': 'Not Found', 'data': f'Beer {beer_id} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to save beer {beer_id}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

    def delete(self, beer_id) -> json:
        """Delete the specified beer."""
        logger.debug(f"Request: {request}, for id: {beer_id}.")

        # Retrieve this beer from the database
        try:
            beer = Beer.get(beer_id)
            logger.debug(f"Retrieved beer: {beer}")

        except Beer.DoesNotExist:
            logger.debug(f"Beer {beer_id} not found.")
            return {'message': 'Not Found', 'data': f'Beer {beer_id} not found.'}, 404
        except PynamoDBException as e:
            error_msg = f"Error attempting to retrieve beer {beer_id}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500

        # Delete the specified beer
        try:
            footprint = f"{beer}"
            beer.delete()
            logger.info(f"Beer {footprint} deleted successfully.")
            logger.debug("End of BeerApi.DELETE")
            return {'message': 'Success', 'data': f'{footprint} deleted successfully.'}, 200

        except PynamoDBException as e:
            error_msg = f"Error attempting to delete beer: {beer}."
            logger.debug(f"{error_msg}\n{e}")
            return {'message': 'Error', 'data': error_msg}, 500
