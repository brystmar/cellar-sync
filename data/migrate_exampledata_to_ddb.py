from backend.global_logger import logger, local
from backend.models import Beverage
from data.example_data import example_data
import time

skipped = 0
count = 0
success = 0
errors = []
beerlist = []

# Create table if necessary
if not Beverage.exists():
    logger.info(f"Creating a new table: {Beverage.Meta.table_name}.")
    Beverage.create_table(wait=True,
                          read_capacity_units=5,
                          write_capacity_units=5)
    logger.info(f"Table created.")

for item in example_data:
    logger.debug(f"Initializing a new Beverage for: {item}")
    beer = Beverage(**item)
    beerlist.append(beer)
    # logger.debug("Beverage initialized.")

logger.info(f"Starting batch save for {len(beerlist)} beers.")
print(f"Starting batch save for {len(beerlist)} beers.")
for beer in beerlist:
    logger.debug(f"Saving beer #{count+1}: {beer}.")
    print(f"Saving beer #{count+1}: {beer.to_dict()}")
    beer.save()

    logger.debug("Success!")
    count += 1

    if not local and count % 20 == 0:
        time.sleep(3)
