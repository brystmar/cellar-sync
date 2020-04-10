from backend.global_logger import logger, local
from backend.config import Config
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute
import json


class Beer(Model):
    class Meta:
        table_name = 'CellarTest'
        region = Config.AWS_REGION
        if local:  # Use the local DynamoDB instance when running locally
            host = 'http://localhost:8008'

    # Primary Attributes
    # `id`: A concatenation of brewery, beer name, year, size, and {batch or bottle date}.
    beer_id = UnicodeAttribute(hash_key=True)

    # Required Attributes
    name = UnicodeAttribute()
    brewery = UnicodeAttribute()
    year = NumberAttribute()
    size = UnicodeAttribute()
    batch = NumberAttribute(null=True)
    bottle_date = UnicodeAttribute(null=True)
    location = UnicodeAttribute(range_key=True)

    # Optional Attributes
    qty = NumberAttribute(null=True)
    style = UnicodeAttribute(null=True)
    specific_style = UnicodeAttribute(null=True)
    untappd = UnicodeAttribute(null=True)
    aging_potential = UnicodeAttribute(null=True)
    trade_value = UnicodeAttribute(null=True)
    for_trade = BooleanAttribute(default=True)
    date_added = NumberAttribute(null=True, default=datetime.timestamp(datetime.utcnow()))
    last_modified = NumberAttribute(null=True, default=datetime.timestamp(datetime.utcnow()))
    note = UnicodeAttribute(null=True)

    def to_dict(self) -> dict:
        """Returns a python dictionary with all attributes of this Beer."""
        return {
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
            "for_trade":       self.for_trade.__str__() if self.for_trade else None,
            "date_added":      self.date_added,
            "last_modified":   self.last_modified,
            "note":            self.note.__str__() if self.note else None
        }

    def to_json(self) -> str:
        """Serializes the output from Beer.to_dict() to JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"Initializing a new instance of the Beer model for {kwargs}.")

        # Construct the concatenated beer_id when not provided:
        #  brewery, beer name, year, size, {bottle date or batch}.  Bottle date preferred.
        if 'beer_id' not in kwargs.keys():
            self.beer_id = f"{kwargs['brewery']}_{kwargs['name']}_{kwargs['year']}_{kwargs['size']}"
            if 'batch' not in kwargs.keys() or kwargs['batch'] == '':
                self.batch = None
                if 'bottle_date' not in kwargs.keys() or kwargs['bottle_date'] == '':
                    # No batch or bottle date
                    self.beer_id += "_None"
                    self.bottle_date = None
                else:
                    self.beer_id += f"_{kwargs['bottle_date']}"
            else:
                self.beer_id += f"_{kwargs['batch']}"
            logger.debug(f"Created a beer_id for this new Beer: {self.beer_id}.")
        else:
            logger.debug(f"Beer already has an id: {kwargs['beer_id']}")
            self.beer_id = kwargs['beer_id']

    def __repr__(self) -> str:
        return f'<Beer | beer_id: {self.beer_id}, qty: {self.qty}, location: {self.location}>'
