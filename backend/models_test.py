from backend.models import Beer
from datetime import datetime
import pytest
import json

default_beer = {
    "beer_id":         "This Is My #4 BeerId",
    "brewery":         "Westbrook",
    "name":            "Gose",
    "year":            2013,
    "size":            "12 oz",
    "location":        "Home",
    "batch":           1,
    "bottle_date":     "2013-06-24",
    "qty":             14,
    "style":           "Sour",
    "specific_style":  "Gose",
    "untappd":         "https://untappd.com/b/westbrook-brewing-co-gose/155824",
    "aging_potential": "Poor",
    "trade_value":     "Low",
    "for_trade":       True,
    "note":            "My go-to when mowing the lawn.",
    "date_added":      "2020-04-10",
    "last_modified":   "2020-04-11"
}


class TestBeerModel:

    def test_required_attributes(self):
        # Must provide values for brewery, beer name, year, size, and location
        with pytest.raises(KeyError):
            beer = Beer()

        # Missing brewery
        with pytest.raises(KeyError):
            beer = Beer(name="Gose",
                        year=2013,
                        size="12 oz",
                        location="Home",
                        bottle_date="2013-06-24",
                        batch=1)

        # Missing name
        with pytest.raises(KeyError):
            beer = Beer(brewery="Westbrook",
                        year=2013,
                        size="12 oz",
                        location="Home",
                        bottle_date="2013-06-24",
                        batch=1)

        # Missing year
        with pytest.raises(KeyError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        size="12 oz",
                        location="Home",
                        bottle_date="2013-06-24",
                        batch=1)

        # Missing size
        with pytest.raises(KeyError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        year=2013,
                        location="Home",
                        bottle_date="2013-06-24",
                        batch=1)

        # Missing location
        with pytest.raises(KeyError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        year=2013,
                        size="12 oz",
                        bottle_date="2013-06-24",
                        batch=1)

        # Year must be int (or convert to int)
        with pytest.raises(ValueError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        year="Nineteen Ninety-Seven",
                        size="12 oz",
                        location="Home",
                        batch=1)

        # Batch must be int (or convert to int)
        with pytest.raises(ValueError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        year=2013,
                        size="12 oz",
                        location="Home",
                        batch="Eskimo")

        # Qty must be int (or convert to int)
        with pytest.raises(ValueError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        year=2013,
                        size="12 oz",
                        location="Home",
                        batch=1,
                        qty="Five")

    def test_beer_id_creation(self):
        # Generate a beer_id when not provided
        #  Ex: brewery_BeerName_year_size_{BottleDate or batch}
        # Should produce a fully-formed concatenated beer_id w/bottle_date
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    bottle_date="2013-06-24")
        assert beer.beer_id == "Westbrook_Gose_2013_12 oz_2013-06-24"

        # Should produce a fully-formed concatenated beer_id w/batch
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1)
        assert beer.beer_id == "Westbrook_Gose_2013_12 oz_1"

        #  When both bottle_date & batch are provided, bottle_date is used
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    bottle_date="2013-06-24",
                    batch=1)
        assert beer.beer_id == "Westbrook_Gose_2013_12 oz_2013-06-24"

        # With batch & bottle date both omitted, the beer_id generated should end with "_None"
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home")
        assert beer.beer_id == "Westbrook_Gose_2013_12 oz_None"

    def test_beer_id(self):
        # When provided with a beer_id, a new one shouldn't be generated
        beer = Beer(beer_id="This Is My #1 BeerId",
                    brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home")
        assert beer.beer_id == "This Is My #1 BeerId"

    def test_datetime_attributes(self):
        # TDA1: When date_added and/or last_modified aren't specified, they should be created
        now = datetime.utcnow()
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1)

        # Type checks
        assert isinstance(beer.date_added, datetime)
        assert isinstance(beer.last_modified, datetime)

        # Since neither value was provided, both should be generated immediately
        #  Difference between `now` and those values should be much less than 1s
        assert (now - beer.date_added).total_seconds() < 1
        assert beer.date_added == beer.last_modified

        # TDA2: Specify date_added as string
        now = datetime.utcnow()
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1,
                    date_added="2020-04-11")

        # Type checks
        assert isinstance(beer.date_added, datetime)
        assert isinstance(beer.last_modified, datetime)

        # Since date_added was provided, it should be well in the past, much longer than 1s
        assert (now - beer.date_added).total_seconds() > 1
        assert (now - beer.last_modified).total_seconds() < 1

        # TDA3: Specify date_added as epoch
        now = datetime.utcnow()
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1,
                    date_added=datetime.utcfromtimestamp(1586622254.147498))

        # Type checks
        assert isinstance(beer.date_added, datetime)
        assert isinstance(beer.last_modified, datetime)

        # Same checks as TDA2
        assert (now - beer.date_added).total_seconds() > 1
        assert (now - beer.last_modified).total_seconds() < 1

        # TDA4: Use an invalid string for date_added
        with pytest.raises(ValueError):
            beer = Beer(brewery="Westbrook",
                        name="Gose",
                        year=2013,
                        size="12 oz",
                        location="Home",
                        batch=1,
                        date_added="Mr. Peanutbutter")

        # TDA5: Specify last_modified, which should be ignored
        now = datetime.utcnow()
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1,
                    last_modified=datetime.utcfromtimestamp(1586631578.640012))

        # Type checks
        assert isinstance(beer.date_added, datetime)
        assert isinstance(beer.last_modified, datetime)

        # Model should ignore the last_modified value and yield the same result as TDA1 above
        assert (now - beer.date_added).total_seconds() < 1
        assert beer.date_added == beer.last_modified

    def test_attribute_changes(self):
        # Create with all available attributes
        beer = Beer(beer_id="This Is My #2 BeerId",
                    brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1,
                    last_modified=datetime.utcfromtimestamp(1586631578.640012))

        # Change some attributes and verify the changes stuck

    def test_model_creation(self):
        # Create with all available attributes using keyword args
        beer = Beer(beer_id="This Is My #3 BeerId",
                    brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home",
                    batch=1,
                    bottle_date="2013-06-24",
                    qty=14,
                    style="Sour",
                    specific_style="Gose",
                    untappd="https://untappd.com/b/westbrook-brewing-co-gose/155824",
                    aging_potential="Poor",
                    trade_value="Low",
                    for_trade=True,
                    note="My go-to when mowing the lawn.",
                    date_added="2020-04-10",
                    last_modified="2020-04-11")

        assert beer.beer_id == "This Is My #3 BeerId"
        assert beer.brewery == "Westbrook"
        assert beer.name == "Gose"
        assert beer.year == 2013
        assert beer.size == "12 oz"
        assert beer.location == "Home"
        assert beer.batch == 1
        assert beer.bottle_date == "2013-06-24"
        assert beer.qty == 14
        assert beer.style == "Sour"
        assert beer.specific_style == "Gose"
        assert beer.untappd == "https://untappd.com/b/westbrook-brewing-co-gose/155824"
        assert beer.aging_potential == "Poor"
        assert beer.trade_value == "Low"
        assert beer.for_trade is True
        assert beer.note == "My go-to when mowing the lawn."
        assert beer.date_added == datetime.fromisoformat("2020-04-10")
        assert (datetime.utcnow() - beer.last_modified).total_seconds() < 1

        # Same test, but created by parsing a dictionary
        beer = Beer(**default_beer)

        assert beer.beer_id == "This Is My #4 BeerId"
        assert beer.brewery == "Westbrook"
        assert beer.name == "Gose"
        assert beer.year == 2013
        assert beer.size == "12 oz"
        assert beer.location == "Home"
        assert beer.batch == 1
        assert beer.bottle_date == "2013-06-24"
        assert beer.qty == 14
        assert beer.style == "Sour"
        assert beer.specific_style == "Gose"
        assert beer.untappd == "https://untappd.com/b/westbrook-brewing-co-gose/155824"
        assert beer.aging_potential == "Poor"
        assert beer.trade_value == "Low"
        assert beer.for_trade is True
        assert beer.note == "My go-to when mowing the lawn."
        assert beer.date_added == datetime.fromisoformat("2020-04-10")
        assert (datetime.utcnow() - beer.last_modified).total_seconds() < 1

    def test_to_dict(self):
        # Full default beer converted to a dictionary
        beer = Beer(**default_beer)
        beer_dict = beer.to_dict()

        assert isinstance(beer_dict, dict)
        assert beer_dict['beer_id'] == "This Is My #4 BeerId"
        assert beer_dict['brewery'] == "Westbrook"
        assert beer_dict['name'] == "Gose"
        assert beer_dict['year'] == 2013
        assert beer_dict['size'] == "12 oz"
        assert beer_dict['location'] == "Home"
        assert beer_dict['batch'] == 1
        assert beer_dict['bottle_date'] == "2013-06-24"
        assert beer_dict['qty'] == 14
        assert beer_dict['style'] == "Sour"
        assert beer_dict['specific_style'] == "Gose"
        assert beer_dict['untappd'] == "https://untappd.com/b/westbrook-brewing-co-gose/155824"
        assert beer_dict['aging_potential'] == "Poor"
        assert beer_dict['trade_value'] == "Low"
        assert beer_dict['for_trade'] is True
        assert beer_dict['note'] == "My go-to when mowing the lawn."

        # The .to_dict() method returns the datetime fields as a `float` epoch
        assert beer_dict['date_added'] == 1586502000.0
        assert isinstance(beer_dict['last_modified'], float)
        
        # When providing the minimum required fields, the optional fields return as None
        beer = Beer(brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    location="Home")
        beer_dict = beer.to_dict()
        
        assert beer_dict['beer_id'] == "Westbrook_Gose_2013_12 oz_None"
        assert beer_dict['brewery'] == "Westbrook"
        assert beer_dict['name'] == "Gose"
        assert beer_dict['year'] == 2013
        assert beer_dict['size'] == "12 oz"
        assert beer_dict['location'] == "Home"
        assert beer_dict['batch'] is None
        assert beer_dict['bottle_date'] is None
        assert beer_dict['qty'] is None
        assert beer_dict['style'] is None
        assert beer_dict['specific_style'] is None
        assert beer_dict['untappd'] is None
        assert beer_dict['aging_potential'] is None
        assert beer_dict['trade_value'] is None
        assert beer_dict['for_trade'] is True  # Defaults to True
        assert beer_dict['note'] is None

        # The .to_dict() method returns the datetime fields as a `float` epoch
        now = datetime.timestamp(datetime.utcnow())
        assert abs(now - beer_dict['date_added']) < 1
        assert abs(now - beer_dict['last_modified']) < 1

    def test_to_json(self):
        # Verify the output is json by calling json.loads() without raising an exception
        beer_json = Beer(**default_beer).to_json()
        assert isinstance(json.loads(beer_json), dict)

    def test_dunders(self):
        # Test the double-underscore methods
        beer = Beer(beer_id="This Is My #4 BeerId",
                    brewery="Westbrook",
                    name="Gose",
                    year=2013,
                    size="12 oz",
                    batch=1,
                    location="Home")

        test_string = beer.__repr__()
        assert isinstance(test_string, str)
        assert "This Is My #4 BeerId" in test_string
        assert "Home" in test_string
