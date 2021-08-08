# Cellar Sync
A basic cellar inventory system for my unwieldy cellar of adult beverages.

This project contains the backend.  See [cellar-sync-ui](http://https://github.com/brystmar/cellar-sync-ui/) for the front end.

# Data Model
Data is structured as a NoSQL document store.  Initially using AWS DynamoDB, though that may change.

### Attributes
* `beverage_id` (`str`) - **Partition Key** (*hash key*).  Concatenation of beverage name, producer, year, size, & bottle date.
* `name` (`str`) *r - Name of the beverage.
* `producer` (`str`) *r - Brewery / winery / meadery / cidery who produced the beverage.
* `year` (`int`) - Calendar year in YYYY format.  For seasonal beverages which cross years, this should be the most-recent year.  Ex: Lambic from the 2017-2018 season is considered 2018.
* `size` (`str`) - Bottle size.  Picklist of the most common formats.
* `bottle_date` (`date`) - Date the beverage was bottled in **YYYY-MM-DD** format.
* `batch` (`str`) - Batch or blend number, from 1-9999.
* `location` (`str`) - Picklist of unique storage locations.
* `style` (`str`) - Overall style of the beverage.
* `specific_style` (`str`) - Subset of `style` for more granular categorization.
* `qty` (`int`) - *Default: 0.* - # of bottles at the current location.
* `qty_cold` (`int`) - *Default: 0.* - Of the above qty, how many are currently chilled?
* `for_trade` (`bool`) - *Default: Yes.* - Is this beverage available for trade?
* `trade_value` (`str`) - [Low, Medium, High] - Basic indication of value in the current trading marketplace.
* `aging_potential` (`str`) - [Poor, Moderate, Strong] - What's the aging potential for this beverage? 
* `untappd` (`str`) - Link to the beverage in question on [Untappd](https://untappd.com/).
* `note` (`str`) - Text field for any additional notes about this beverage. 
* `date_added` (`str`) - System field, created automatically.  Stored as an [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) string in UTC.
* `last_modified` (`str`) - System field, updated automatically.  Stored as an [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) string in UTC.
