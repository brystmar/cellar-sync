from backend.global_logger import logger, local
from backend.config import Config
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, \
    UTCDateTimeAttribute, ListAttribute, MapAttribute

# === REFACTOR PLAN ===
# Structure: beverage > vintage (<-> location)
#
# beverage
# - beverage_id
# - producer
# - name
# - style
# - specific style
# - trade value
# - aging potential
# - vintages
# - date added
# - last modified

# location
# - name ==> defaults to Home, user can add more locations
# - qty
# - qty cold
# - note
# - display order

# vintage
# --> defaults to an unnamed vintage, user can add more vintages
# - bottle date (accepts YYYY, YYYY-MM, YYYY-MM-DD)
# - batch (optional)
# - size
# - for trade
# - locations (select created locations only)
# - untappd link
# - note
# - display order
# - date added
# - last modified


class Location(MapAttribute):
    """
    Each vintage of a beverage can be segmented by its location.
    Quantity is set at this level.
    """
    name = UnicodeAttribute(null=False, default="Home")
    qty = NumberAttribute(null=True, default=0)
    qty_cold = NumberAttribute(null=True, default=0)
    note = UnicodeAttribute(null=True)
    display_order = NumberAttribute(null=False, default=0)

    def to_dict(self) -> dict:
        """
        Convert this location to a dictionary.
        """
        return {
            "name":          self.name.__str__(),
            "qty":           int(self.qty) if self.qty else 0,
            "qty_cold":      int(self.qty_cold) if self.qty_cold else 0,
            "note":          self.note.__str__() if self.note else None,
            "display_order": int(self.display_order) if self.display_order else 0
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Type check: qty
        if 'qty' in kwargs.keys():
            try:
                self.qty = int(kwargs['qty'])
            except ValueError as e:
                logger.debug(f"Qty must be an integer.\n{e}")
                raise ValueError(f"Qty must be an integer.\n{e}")

        # Type check: qty_cold
        if 'qty_cold' in kwargs.keys():
            try:
                self.qty_cold = int(kwargs['qty_cold'])
            except ValueError as e:
                logger.debug(f"Qty_cold must be an integer.\n{e}")
                raise ValueError(f"Qty_cold must be an integer.\n{e}")

    def __repr__(self) -> str:
        return f'<Location name: {self.name}, qty: {self.qty}, qty_cold: {self.qty_cold}' \
               f'added: {self.date_added}>'


class Vintage(MapAttribute):
    """
    Details about a specific vintage for a particular Beverage.
    Beverages contain a list of Vintages.  One unnamed Vintage is created by default.
    """
    bottle_date = UnicodeAttribute(null=True)
    batch = NumberAttribute(null=True)
    size = UnicodeAttribute(null=True)
    for_trade = BooleanAttribute(null=True, default=True)
    locations = ListAttribute(null=False, of=Location)

    # Reference attributes
    untappd = UnicodeAttribute(null=True)
    note = UnicodeAttribute(null=True)
    display_order = NumberAttribute(null=False, default=0)
    date_added = UTCDateTimeAttribute(default=datetime.utcnow())
    last_modified = UTCDateTimeAttribute(default=datetime.utcnow())

    def to_dict(self, dates_as_epoch=False) -> dict:
        """
        Convert this vintage (including any locations) to a python dictionary.
        """
        # Convert all associated locations to a dictionary
        vintage_locations = []
        for location in self.locations:
            if isinstance(location, dict):
                # logger.debug(f"Step: {step}, type: {type(step)}")
                vintage_locations.append(location)
            elif isinstance(location, Location):
                vintage_locations.append(location.to_dict())
            else:
                raise TypeError(f"Invalid type for provided location: {location} "
                                f"(type {type(location)}).")

        output = {
            "bottle_date":   self.bottle_date.__str__() if self.bottle_date else None,
            "batch":         int(self.batch) if self.batch else None,
            "size":          self.size.__str__() if self.size else None,
            "for_trade":     self.for_trade,
            "locations":     vintage_locations,
            "untappd":       self.untappd.__str__() if self.untappd else None,
            "note":  self.note.__str__() if self.note else None,
            "display_order": int(self.display_order) if self.display_order else 0,
            "date_added":    self.date_added.timestamp() * 1000,  # JS timestamps are in ms
            "last_modified": self.last_modified.timestamp() * 1000
        }

        if not dates_as_epoch:
            output['date_added'] = self.date_added.__str__()
            output['last_modified'] = self.last_modified.__str__()

        return output

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Type check: batch
        if 'batch' in kwargs.keys():
            try:
                if self.batch and self.batch != "":
                    self.batch = int(kwargs['batch'])
                if self.batch == "":
                    self.batch = None
            except ValueError as e:
                logger.debug(f"Batch number must be an integer.\n{e}")
                raise ValueError(f"Batch number must be an integer.\n{e}")

    def __repr__(self) -> str:
        vintage_locations = []
        for location in self.locations:
            vintage_locations.append(location.__repr__())

        return f'<Vintage bottled: {self.bottle_date}, batch: {self.batch}, ' \
               f'added: {self.date_added}, locations: {vintage_locations}>'


class Beverage(Model):
    class Meta:
        table_name = 'Cellar'
        region = Config.AWS_REGION
        if local:  # Use the local DynamoDB instance when running locally
            host = 'http://localhost:8008'

    # Primary Attributes
    # `beverage_id`: Lowercase concatenation of producer & beverage
    #  *** Examples ***
    #   Cantillon: Lou Pepe Framboise
    #   Goose Island: Bourbon County Brand Stout
    beverage_id = UnicodeAttribute(hash_key=True)

    # Required Attributes
    producer = UnicodeAttribute(null=False, range_key=True)
    name = UnicodeAttribute(null=False)
    vintages = ListAttribute(null=False, of=Vintage)

    # Optional Attributes
    style = UnicodeAttribute(null=True)
    specific_style = UnicodeAttribute(null=True)
    trade_value = NumberAttribute(null=True, default=0)
    aging_potential = NumberAttribute(null=True, default=2)

    # Reference Attributes
    note = UnicodeAttribute(null=True)
    date_added = UTCDateTimeAttribute(default=datetime.utcnow())
    last_modified = UTCDateTimeAttribute(default=datetime.utcnow())

    def to_dict(self, dates_as_epoch=False) -> dict:
        """
        Return a dictionary with all attributes.
        Dates return as epoch (default) or in ISO format.
        """
        # Convert all associated vintages to a dictionary
        beverage_vintages = []
        for vintage in self.vintages:
            if isinstance(vintage, dict):
                # logger.debug(f"Step: {step}, type: {type(step)}")
                beverage_vintages.append(vintage)
            elif isinstance(vintage, Vintage):
                beverage_vintages.append(vintage.to_dict(dates_as_epoch=dates_as_epoch))
            else:
                raise TypeError(f"Invalid type for provided vintage: {vintage} "
                                f"(type {type(vintage)}).")

        output = {
            "beverage_id":     self.beverage_id.__str__(),
            "producer":        self.producer.__str__(),
            "name":            self.name.__str__(),
            "vintages":        beverage_vintages,
            "style":           self.style.__str__() if self.style else None,
            "specific_style":  self.specific_style.__str__() if self.specific_style else None,
            "aging_potential": int(self.aging_potential) if self.aging_potential else None,
            "trade_value":     int(self.trade_value) if self.trade_value else None,
            "note":            self.note.__str__() if self.note else None,
            "date_added":      self.date_added.timestamp() * 1000,  # JS timestamps are in ms
            "last_modified":   self.last_modified.timestamp() * 1000
        }

        if not dates_as_epoch:
            output['date_added'] = self.date_added.__str__()
            output['last_modified'] = self.last_modified.__str__()

        return output

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Replace empty strings with None
        # Construct the concatenated beverage_id when not provided
        if 'beverage_id' not in kwargs.keys():
            # Need to create a beverage_id for this beverage
            self.beverage_id = f"{kwargs['producer']}: {kwargs['name']}"
            logger.debug(f"Created a beverage_id for this new Beverage: {self.beverage_id}.")

        # Adjust last_modified due to JS working in milliseconds
        if 'last_modified' in kwargs.keys():
            # Accept an epoch (`float` or `int`) for date_added
            if isinstance(self.last_modified, (float, int)):
                self.last_modified = datetime.utcfromtimestamp(kwargs['last_modified'] / 1000)
            else:
                # Assume a string was provided and parse a datetime object from that
                try:
                    self.last_modified = datetime.fromisoformat(str(self.last_modified))
                except (TypeError, ValueError) as e:
                    logger.debug(f"Provided value for last_modified: {self.last_modified}, "
                                 f"{type(self.last_modified)} cannot be converted to datetime.")
                    raise ValueError(f"Value for last_modified must be an epoch (float/int) or "
                                     f"an ISO-formatted string. {e}")
        else:
            self.last_modified = datetime.utcnow()

        # Type & value checks for date_added
        if 'date_added' in kwargs.keys():
            # Accept an epoch (`float` or `int`) for date_added
            if isinstance(self.date_added, (float, int)):
                self.date_added = datetime.utcfromtimestamp(kwargs['date_added'] / 1000)
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

    def __repr__(self) -> str:
        beverage_vintages = []
        for vintage in self.vintages:
            beverage_vintages.append(vintage.__repr__())

        return f'<Beverage | bev_id: {self.beverage_id}, added: {self.date_added}>'


class PicklistValue(MapAttribute):
    """Individual value within each Picklist.values list"""
    # Primary attributes
    value = UnicodeAttribute()

    # For nesting a dependent picklist, i.e. `style` --> `specific_style`
    dependent_values = ListAttribute(null=True)

    # For lists where the order matters but sorting is hard, i.e. `size`
    display_order = NumberAttribute(null=True)

    def to_dict(self) -> dict:
        output = {
            "value": self.value.__str__()
        }

        if self.dependent_values:
            output['dependent_values'] = self.dependent_values

        if self.display_order:
            output['display_order'] = self.display_order.__str__()

        return output


class Picklist(Model):
    class Meta:
        table_name = 'CellarPicklists'
        region = Config.AWS_REGION
        if local:  # Use the local DynamoDB instance when running locally
            host = 'http://localhost:8008'

    # `list_name`: The attribute whose values this list contains
    list_name = UnicodeAttribute(hash_key=True)
    list_values = ListAttribute(of=PicklistValue)
    last_modified = UnicodeAttribute(default=datetime.utcnow())

    def to_dict(self) -> dict:
        """Convert this Picklist (and any children) to a python dictionary."""

        value_list = []
        if self.list_values:
            for value in self.list_values:
                if isinstance(value, dict):
                    value_list.append(value)
                elif isinstance(value, PicklistValue):
                    value_list.append(value.to_dict())
                else:
                    raise TypeError(f"Invalid type for `list_values` in Picklist.to_dict:"
                                    f"{type(self.list_values)}, {self.list_values}")

        output = {
            "list_name":     self.list_name.__str__(),
            "list_values":   value_list,
            "last_modified": self.last_modified.timestamp() * 1000  # JS timestamps are in ms
        }

        return output

    def __repr__(self) -> str:
        return f'<Picklist values for {self.list_name}>'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Type check: last_modified
        # Accept `str` or an epoch (`float`, `int`) for last_modified
        # logger.debug(f"Type check for last_modified of picklist: {self.list_name}")
        # logger.debug(f"{type(self.last_modified)}, {self.last_modified}")
        # if !isinstance(self.last_modified, datetime):
        if isinstance(self.last_modified, (float, int)):
            self.last_modified = datetime.utcfromtimestamp(kwargs['last_modified'] / 1000)
        else:
            # Assume a string was provided and parse a datetime object from that
            try:
                self.last_modified = datetime.fromisoformat(str(self.last_modified))
            except (TypeError, ValueError) as e:
                logger.debug(f"Provided value for last_modified: {self.last_modified}, "
                             f"{type(self.last_modified)} cannot be converted to datetime.")
                raise ValueError(f"Value for last_modified must be an epoch (float/int) or "
                                 f"an iso-formatted string. {e}")
        # logger.debug(f"Picklist class initialized.")
