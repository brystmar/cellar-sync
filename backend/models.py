from backend.global_logger import logger
from backend.config import Config
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute, \
    BooleanAttribute
import json


class Beer(Model):
    class Meta:
        table_name = 'Cellar'
        region = Config.AWS_REGION
        # if local:  # Use the local DynamoDB instance when running locally
        #     host = 'http://localhost:8008'

    # Primary Attributes
    # `id`: A concatenation of beer name, brewery, year, size, & bottle date.
    beer_id = UnicodeAttribute(hash_key=True)

    # Required Attributes
    name = UnicodeAttribute()
    brewery = UnicodeAttribute()
    year = NumberAttribute()
    # batch = NumberAttribute(null=True)
    batch_str = UnicodeAttribute(null=True)
    size = UnicodeAttribute()
    bottle_date = UnicodeAttribute(null=True)
    location = UnicodeAttribute(range_key=True)

    # Optional Attributes
    qty = NumberAttribute(null=True)
    style = UnicodeAttribute(null=True)
    specific_style = UnicodeAttribute(null=True)
    untappd = UnicodeAttribute(null=True)
    # aging_potential = UnicodeAttribute(null=True)
    # trade_value = UnicodeAttribute(null=True)
    for_trade = BooleanAttribute(default=True)
    date_added = NumberAttribute(null=True, default=datetime.timestamp(datetime.utcnow()))
    note = UnicodeAttribute(null=True)

    def to_dict(self) -> dict:
        """Returns a python dictionary with all attributes of this Beer."""
        return {
            "id":              self.beer_id.__str__(),
            "name":            self.name.__str__(),
            "brewery":         self.brewery.__str__(),
            "year":            int(self.year),
            # "batch":           int(self.batch),
            "batch_str":       self.batch_str.__str__(),
            "size":            self.size.__str__(),
            "bottle_date":     self.bottle_date.__str__(),
            "location":        self.location.__str__(),
            "date_added":      self.date_added.__str__(),
            "style":           self.style.__str__(),
            "specific_style":  self.specific_style.__str__(),
            "qty":             int(self.qty),
            "untappd":         self.untappd.__str__(),
            # "aging_potential": self.aging_potential.__str__(),
            # "trade_value":     self.trade_value.__str__(),
            "for_trade":       self.for_trade.__str__(),
            "note":            self.note.__str__()
        }

    def to_json(self) -> str:
        """Serializes the output from Beer.to_dict() to JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=True)

    def __init__(self, needs_id=False, beer_id=beer_id, name=name, brewery=brewery, year=year, size=size,
                 bottle_date=bottle_date, location=location, style=style, batch_str=batch_str,
                 substyle=specific_style, qty=qty, untappd=untappd, for_trade=for_trade, note=note,
                 **attrs):
        # date_added=date_added, trade_value=trade_value, batch=batch,
        #  aging_potential=aging_potential,
        super().__init__(**attrs)
        # logger.debug("Initializing a new instance of the Beer model.")

        # Construct the concatenated id when it's not provided
        #  Concatenation of name, brewery, year, size, and (bottle date || batch).
        #  Bottle date preferred over batch.
        # logger.debug(f"id: {beer_id}, type: {type(beer_id)}, str: {beer_id.__str__()}, str2: {str(beer_id)}")
        # logger.debug(str(f"{name}_{brewery}_{year}_{size}_{bottle_date}, {batch_str}, {location},"
        #                  f"{date_added}, {qty}"))
        if needs_id:
            logger.debug("This new Beer needs an id.")
            logger.debug(f"bottle_date: {bottle_date}, type: {type(bottle_date)}")
            logger.debug(f"style: {style}, type: {type(style)}")
            if bottle_date:
                self.beer_id = f"{name}_{brewery}_{year}_{size}_{bottle_date}"
            # elif batch:
            #     self.id = f"{name}_{brewery}_{year}_{size}_{batch}"
            else:
                self.beer_id = f"{name}_{brewery}_{year}_{size}_{batch_str}"
        else:
            self.beer_id = beer_id

        """
        self.name = self._null_handler(name)
        self.brewery = self._null_handler(brewery)
        self.year = self._null_handler(year)
        # self.batch = self._null_handler(batch)
        self.batch_str = self._null_handler(batch_str)
        self.size = self._null_handler(size)
        self.bottle_date = self._null_handler(bottle_date)
        self.location = self._null_handler(location)
        self.date_added = datetime.timestamp(datetime.utcnow())
        self.style = self._null_handler(style)
        self.specific_style = self._null_handler(substyle)
        self.qty = self._null_handler(qty)
        self.untappd = self._null_handler(untappd)
        # self.aging_potential = self._null_handler(aging_potential)
        # self.trade_value = self._null_handler(trade_value)
        self.for_trade = self._null_handler(for_trade)
        self.note = self._null_handler(note)
        """

    def _null_handler(self, attr):
        """
        Nulls in the ORM should be represented as a NoneType object instead of:
          <pynamodb.attributes.UnicodeAttribute object at 0x7f9e104d4c18>
        """
        # logger.debug(f"Starting Beer._null_handler for {attr}, type: {type(attr)}")
        if isinstance(attr, (UnicodeAttribute, str)):
            if not attr:
                return None
        elif isinstance(attr, (NumberAttribute, int, float)):
            if not attr:
                return 0
        elif isinstance(attr, (UTCDateTimeAttribute, datetime)):
            if not attr:
                return datetime.utcnow()
        elif isinstance(attr, (BooleanAttribute, bool)):
            if not attr:
                return True

        # logger.debug("No matches, returning the attribute untouched.")
        return attr

    def __repr__(self) -> str:
        return f'<Beer | id: {self.beer_id}, name: {self.name}, brewery: {self.brewery}, ' \
               f'year: {self.year}, batch: {self.batch_str}, size: {self.size}, ' \
               f'bottled: {self.bottle_date}, location: {self.location}>'
