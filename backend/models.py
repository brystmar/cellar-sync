from backend.global_logger import logger, local
from backend.config import Config
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute, \
    BooleanAttribute
import json


class Beer(Model):
    class Meta:
        table_name = 'Cellar'
        region = Config.aws_region
        if local:  # Use the local DynamoDB instance when running locally
            host = 'http://localhost:8008'

    # Primary Attributes
    # `id`: A concatenation of beer name, brewery, year, size, & bottle date.
    id = UnicodeAttribute(hash_key=True)

    # Required Attributes
    name = UnicodeAttribute()
    brewery = UnicodeAttribute()
    year = NumberAttribute()
    batch = NumberAttribute(null=True)
    batch_str = UnicodeAttribute(null=True)
    size = UnicodeAttribute()
    bottle_date = UTCDateTimeAttribute(null=True)
    location = UnicodeAttribute(range_key=True)

    # Optional Attributes
    date_added = UTCDateTimeAttribute(null=True)
    style = UnicodeAttribute(null=True)
    specific_style = UnicodeAttribute(null=True)
    qty = NumberAttribute(null=True)
    untappd = UnicodeAttribute(null=True)
    aging_potential = UnicodeAttribute(null=True)
    trade_value = UnicodeAttribute(null=True)
    for_trade = BooleanAttribute(default=True)
    note = UnicodeAttribute(null=True)

    def to_dict(self) -> dict:
        """Returns a python dictionary with all attributes of this Beer."""
        return {
            "id":              self.id.__str__(),
            "name":            self.name.__str__(),
            "brewery":         self.brewery.__str__(),
            "year":            int(self.year),
            "batch":           int(self.batch),
            "batch_str":       self.batch.__str__(),
            "size":            self.size.__str__(),
            "bottle_date":     self.bottle_date.__str__(),
            "location":        self.location.__str__(),
            "date_added":      self.date_added.__str__(),
            "style":           self.style.__str__(),
            "specific_style":  self.specific_style.__str__(),
            "qty":             int(self.qty),
            "untappd":         self.untappd.__str__(),
            "aging_potential": self.aging_potential.__str__(),
            "trade_value":     self.trade_value.__str__(),
            "for_trade":       self.for_trade.__str__(),
            "note":            self.note.__str__()
        }

    def to_json(self) -> str:
        """Serializes the output from Beer.to_dict() to JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=True)

    def __init__(self, id=id, name=name, brewery=brewery, year=year, batch=batch, batch_str=batch_str, size=size,
                 bottle_date=bottle_date, location=location, date_added=date_added, style=style,
                 substyle=specific_style, qty=qty, untappd=untappd, aging_potential=aging_potential,
                 trade_value=trade_value, for_trade=for_trade, note=note, **attrs):
        super().__init__(**attrs)
        logger.debug("Initializing a new instance of the Beer model.")

        # Construct the concatenated id when it's not provided
        #  Concatenation of name, brewery, year, size, and (bottle date || batch).
        #  Bottle date preferred over batch.
        if id is None:
            logger.debug("id not provided.")
            if bottle_date:
                id = str(name + brewery + year + size + bottle_date)
            else:
                id = str(name + brewery + year + size + batch)

        self.id = id
        self.name = name
        self.brewery = brewery
        self.year = year
        self.batch = batch
        self.batch_str = batch_str
        self.size = size
        self.bottle_date = bottle_date
        self.location = location
        self.date_added = date_added
        self.style = style
        self.specific_style = substyle
        self.qty = qty
        self.untappd = untappd
        self.aging_potential = aging_potential
        self.trade_value = trade_value
        self.for_trade = for_trade
        self.note = note

    def __repr__(self) -> str:
        return f'<Beer | id: {self.id}, name: {self.name}, brewery: {self.brewery}, ' \
               f'year: {self.year}, batch: {self.batch}, size: {self.size}, ' \
               f'bottled: {self.bottle_date}, location: {self.location}>'
