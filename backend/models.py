from backend.global_logger import logger, local
from backend.config import Config
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, \
    UTCDateTimeAttribute
import json


class Beer(Model):
    class Meta:
        # table_name = 'CellarTest'
        table_name = 'Cellar'
        region = Config.AWS_REGION
        if local:  # Use the local DynamoDB instance when running locally
            host = 'http://localhost:8008'

    # Primary Attributes
    # `beer_id`: A concatenation of brewery, beer name, year, size, and {batch or bottle date}.
    beer_id = UnicodeAttribute(hash_key=True)

    # Required Attributes
    brewery = UnicodeAttribute()
    name = UnicodeAttribute()
    year = NumberAttribute()
    size = UnicodeAttribute()
    location = UnicodeAttribute(range_key=True)
    batch = NumberAttribute(null=True)
    bottle_date = UnicodeAttribute(null=True)

    # Optional Attributes
    qty = NumberAttribute(null=True)
    style = UnicodeAttribute(null=True)
    specific_style = UnicodeAttribute(null=True)
    untappd = UnicodeAttribute(null=True)
    aging_potential = UnicodeAttribute(null=True)
    trade_value = UnicodeAttribute(null=True)
    for_trade = BooleanAttribute(default=True)
    note = UnicodeAttribute(null=True)

    # date_added should always be <= last_modified
    date_added = UTCDateTimeAttribute(default=datetime.utcnow())
    last_modified = UTCDateTimeAttribute(default=datetime.utcnow())

    def to_dict(self, dates_as_epoch=False) -> dict:
        """
        Returns a dictionary with all attributes.  Dates return as epoch (default) or in ISO format.
        """

        output = {
            "beer_id":         self.beer_id.__str__(),
            "name":            self.name.__str__(),
            "brewery":         self.brewery.__str__(),
            "year":            int(self.year),
            "batch":           int(self.batch) if self.batch else None,
            "size":            self.size.__str__(),
            "bottle_date":     self.bottle_date.__str__() if self.bottle_date else None,
            "location":        self.location.__str__(),
            "style":           self.style.__str__() if self.style else None,
            "specific_style":  self.specific_style.__str__() if self.specific_style else None,
            "qty":             int(self.qty) if self.qty else None,
            "untappd":         self.untappd.__str__() if self.untappd else None,
            "aging_potential": self.aging_potential.__str__() if self.aging_potential else None,
            "trade_value":     self.trade_value.__str__() if self.trade_value else None,
            "for_trade":       self.for_trade if self.for_trade else True,
            "date_added":      self.date_added.timestamp() * 1000,  # JS timestamps are in ms
            "last_modified":   self.last_modified.timestamp() * 1000,
            "note":            self.note.__str__() if self.note else None
        }

        if not dates_as_epoch:
            output['date_added'] = self.date_added.__str__()
            output['last_modified'] = self.last_modified.__str__()

        return output

    def to_json(self, dates_as_epoch=True) -> str:
        """Serializes the output from Beer.to_dict() to JSON."""
        return json.dumps(self.to_dict(dates_as_epoch=dates_as_epoch))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"Initializing a new instance of the Beer model for {kwargs}.")
        # Construct the concatenated beer_id when not provided:
        #  brewery, beer name, year, size, {bottle date or batch}.  Bottle date preferred.
        if 'beer_id' not in kwargs.keys():
            # Need to create a beer_id for this beer
            self.beer_id = f"{kwargs['brewery']}_{kwargs['name']}_{kwargs['year']}_{kwargs['size']}"
            if 'batch' in kwargs.keys() and 'bottle_date' in kwargs.keys():
                # If both bottle_date and batch are provided, prefer bottle_date
                self.beer_id += f"_{kwargs['bottle_date']}"

            elif 'batch' not in kwargs.keys() or kwargs['batch'] == '':
                # Batch is not provided
                self.batch = None
                if 'bottle_date' not in kwargs.keys() or kwargs['bottle_date'] == '':
                    # When no batch or bottle_date is provided, append "_None"
                    self.beer_id += "_None"
                    self.bottle_date = None
                else:
                    # Bottle_date is provided
                    self.beer_id += f"_{kwargs['bottle_date']}"
            else:
                # Use batch when bottle_date isn't provided
                self.beer_id += f"_{kwargs['batch']}"
            logger.debug(f"Created a beer_id for this new Beer: {self.beer_id}.")

        # Must provide a location
        if 'location' not in kwargs.keys() or kwargs['location'] is None:
            logger.debug(f"No value for location provided, raising KeyError.")
            raise KeyError("Location is required.")

        # Type check: Year
        try:
            self.year = int(kwargs['year'])
        except ValueError as e:
            logger.debug(f"Year must be an integer.\n{e}")
            raise ValueError(f"Year must be an integer.\n{e}")

        # Type check: Batch
        if 'batch' in kwargs.keys():
            try:
                self.batch = int(kwargs['batch'])
            except ValueError as e:
                logger.debug(f"Batch number must be an integer.\n{e}")
                raise ValueError(f"Batch number must be an integer.\n{e}")

        # Type check: Qty
        if 'qty' in kwargs.keys():
            try:
                self.qty = int(kwargs['qty'])
            except ValueError as e:
                logger.debug(f"Qty must be an integer.\n{e}")
                raise ValueError(f"Qty must be an integer.\n{e}")

        # Set last_modified if it's not included
        if 'last_modified' not in kwargs.keys():
            self.last_modified = datetime.utcnow()

        # # Type & value checks for date_added
        if 'date_added' in kwargs.keys():
            # Accept an epoch (`float` or `int`) for date_added
            if isinstance(self.date_added, (float, int)):
                self.date_added = datetime.utcfromtimestamp(kwargs['date_added'])
            else:
                # Assume a string was provided and parse a datetime object from that
                try:
                    self.date_added = datetime.fromisoformat(str(self.date_added))
                except (TypeError, ValueError) as e:
                    logger.debug(f"Provided value for date_added: {self.date_added}, "
                                 f"{type(self.date_added)} cannot be converted to datetime.")
                    raise ValueError(f"Value for date_added must be an epoch (float/int) or "
                                     f"an iso-formatted string. {e}")

            # Ensure date_added is always <= last_modified
            if self.date_added > self.last_modified:
                self.last_modified = self.date_added
        else:
            # When date_added is not provided
            self.date_added = self.last_modified or datetime.utcnow()

    def __repr__(self) -> str:
        return f'<Beer | beer_id: {self.beer_id}, qty: {self.qty}, location: {self.location}>'
