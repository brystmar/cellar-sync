# Cellar Sync
Basic cellar inventory management for bored tech workers with an unwieldy cellar.

This project only contains the backend.  UI here: https://github.com/brystmar/cellar-sync-ui/

# Data Model
Data is structured as a NoSQL document store.  Initially using AWS DynamoDB, though that may change.

### Attributes
* `id` (`str`) - **Partition Key (aka Hash Key)**.  Concatenation of beer name, brewery, year, size, & bottle date.
* `name` (`str`) *r
* `brewery` (`str`)
* `year` (`int`)
* `size` (`str`)
* `batch` (`int`)
* `bottle_date` (`date`)
* `date_added` (`date`)
* `location` (`str`) - **Sort Key (aka Range Key)**
* `style` (`str`)
* `substyle` (`str`)
* `qty` (`int`)
* `untappd` (`str`) - Link to the beer in question on Untappd
* `aging_potential` (`str`) - [Low, Medium, High]
* `trade_value` (`str`) - [Low, Medium, High]
* `for_trade` (`bool`)
