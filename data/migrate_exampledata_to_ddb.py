from backend.global_logger import logger
from backend.models import Beer
from data.example_data import example_data
from pynamodb.exceptions import PynamoDBException
from data.errors import error_ids

skipped = 0
count = 0
success = 0
errors = []
for item in example_data:
    oldId = f"{item['name']}_{item['brewery']}_{item['year']}_{item['size']}_{item['bottle_date']}"
    if oldId in error_ids:
        skipped += 1
        count += 1
        continue

    logger.debug(f"Starting beer #{count + 1}...")
    # Create a Beer object for each item in the list
    logger.debug(f"Initializing new Beer object for: {item}")
    beer = Beer(needs_id=True,
                name=item['name'],
                brewery=item['brewery'],
                year=item['year'],
                batch_str=item['batch_str'],
                size=item['size'],
                bottle_date=item['bottle_date'],
                location=item['location'],
                qty=item['qty'],
                style=item['style'],
                substyle=item['specific_style'],
                untappd=item['untappd'],
                for_trade=item['for_trade'],
                note=item['note'])

    logger.debug("Beer initialized.")
    # logger.debug(f"{type(beer.bottle_date)}, {beer.bottle_date}")
    # logger.debug(f"deserialized bottle_date: {beer.bottle_date.deserialize(item['bottle_date'])}")

    # Save to the database
    try:
        logger.debug(f"Attempting to save... {beer}")
        logger.debug(f"{beer.to_dict()}")
        # beer.save()
        # logger.debug(f"Successfully saved Beer... {beer}.")
        success += 1

    except PynamoDBException as e:
        logger.debug(f"Error saving Beer {beer}.")
        logger.debug(e)
        errors.append(beer)

    if count > 50 or success > 5:
        break
    else:
        count += 1

logger.debug(f"Read {count} items from the list.")
logger.debug(f"Saved: {success}, skipped: {skipped}, new errors: {len(errors)}.")
if errors:
    for error in errors:
        logger.debug(error)
