from backend.models import Beverage
from datetime import datetime
import pytest


default_beverage = {
    "beverage_id":     "This Is My #4 BeverageId",
    "producer":        "Westbrook",
    "name":            "Gose",
    "year":            2013,
    "size":            "12 oz",
    "location":        "Home",
    "batch":           1,
    "bottle_date":     "2013-06-24",
    "qty":             14,
    "qty_cold":        9,
    "style":           "Sour",
    "specific_style":  "Gose",
    "untappd":         "https://untappd.com/b/westbrook-brewing-co-gose/155824",
    "aging_potential": 3,
    "trade_value":     3,
    "for_trade":       True,
    "note":            "My go-to when mowing the lawn.",
    "date_added":      datetime.fromisoformat("2020-04-10"),
    "last_modified":   datetime.fromisoformat("2020-04-11")
}


class TestBeverageModel:

    def test_required_attributes(self):
        # Must provide values for producer, beverage name, year, size, and location
        with pytest.raises(KeyError):
            beverage = Beverage()

        # Missing producer
        with pytest.raises(KeyError):
            beverage = Beverage(name="Gose",
                                year=2013,
                                size="12 oz",
                                location="Home",
                                bottle_date="2013-06-24",
                                batch=1)

        # Missing name
        with pytest.raises(KeyError):
            beverage = Beverage(producer="Westbrook",
                                year=2013,
                                size="12 oz",
                                location="Home",
                                bottle_date="2013-06-24",
                                batch=1)

        # Missing year
        with pytest.raises(KeyError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                size="12 oz",
                                location="Home",
                                bottle_date="2013-06-24",
                                batch=1)

        # Missing size
        with pytest.raises(KeyError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year=2013,
                                location="Home",
                                bottle_date="2013-06-24",
                                batch=1)

        # Missing location
        with pytest.raises(KeyError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year=2013,
                                size="12 oz",
                                bottle_date="2013-06-24",
                                batch=1)

        # Year must be int (or convert to int)
        with pytest.raises(ValueError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year="Nineteen Ninety-Seven",
                                size="12 oz",
                                location="Home",
                                batch=1)

        # Batch must be int (or convert to int)
        with pytest.raises(ValueError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year=2013,
                                size="12 oz",
                                location="Home",
                                batch="Eskimo")

        # Qty must be int (or convert to int)
        with pytest.raises(ValueError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year=2013,
                                size="12 oz",
                                location="Home",
                                batch=1,
                                qty="Five")

        # Qty_cold must be int (or convert to int)
        with pytest.raises(ValueError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year=2013,
                                size="12 oz",
                                location="Home",
                                batch=1,
                                qty_cold="Five")

    def test_beverage_id_creation(self):
        # Generate a beverage_id when not provided
        #  Ex: producer_BeverageName_year_size_{BottleDate or batch}
        # Should produce a fully-formed concatenated beverage_id w/bottle_date
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            bottle_date="2013-06-24")
        assert beverage.beverage_id == "Westbrook_Gose_2013_12 oz_2013-06-24"

        # Should produce a fully-formed concatenated beverage_id w/batch
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1)
        assert beverage.beverage_id == "Westbrook_Gose_2013_12 oz_1"

        #  When both bottle_date & batch are provided, bottle_date is used
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            bottle_date="2013-06-24",
                            batch=1)
        assert beverage.beverage_id == "Westbrook_Gose_2013_12 oz_2013-06-24"

        # With batch & bottle date both omitted, the beverage_id generated should end with "_None"
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home")
        assert beverage.beverage_id == "Westbrook_Gose_2013_12 oz_None"

    def test_beverage_id(self):
        # When provided with a beverage_id, a new one shouldn't be generated
        beverage = Beverage(beverage_id="This Is My #1 BeverageId",
                            producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home")
        assert beverage.beverage_id == "This Is My #1 BeverageId"

    def test_datetime_attributes(self):
        # TDA1: When date_added and/or last_modified aren't specified, they should be created
        now = datetime.utcnow()
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1)

        # Type checks
        assert isinstance(beverage.date_added, datetime)
        assert isinstance(beverage.last_modified, datetime)

        # Since neither value was provided, both should be generated immediately
        #  Difference between `now` and those values should be well below 1s
        assert (now - beverage.date_added).total_seconds() < 1

        # Difference between date_added and last_modified should be well below 1s
        assert (beverage.last_modified - beverage.date_added).total_seconds() < 1

        # TDA2: Specify date_added as string
        now = datetime.utcnow()
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1,
                            date_added="2020-04-11")

        # Type checks
        assert isinstance(beverage.date_added, datetime)
        assert isinstance(beverage.last_modified, datetime)

        # Since date_added was provided, it should be well in the past, much longer than 1s
        assert (now - beverage.date_added).total_seconds() > 1
        assert (now - beverage.last_modified).total_seconds() < 1

        # TDA3: Specify date_added as epoch
        now = datetime.utcnow()
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1,
                            date_added=datetime.utcfromtimestamp(1586622254.147498))

        # Type checks
        assert isinstance(beverage.date_added, datetime)
        assert isinstance(beverage.last_modified, datetime)

        # Same checks as TDA2
        assert (now - beverage.date_added).total_seconds() > 1
        assert (now - beverage.last_modified).total_seconds() < 1

        # TDA4: Use an invalid string for date_added
        with pytest.raises(ValueError):
            beverage = Beverage(producer="Westbrook",
                                name="Gose",
                                year=2013,
                                size="12 oz",
                                location="Home",
                                batch=1,
                                date_added="Mr. Peanutbutter")

        # TDA5: Specify last_modified, which should be ignored
        now = datetime.utcnow()
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1,
                            last_modified=datetime.utcfromtimestamp(1586631578.640012))

        # Type checks
        assert isinstance(beverage.date_added, datetime)
        assert isinstance(beverage.last_modified, datetime)

        # Model should ignore the last_modified value and yield the same result as TDA1 above
        assert (now - beverage.date_added).total_seconds() < 1

        # Difference between date_added and last_modified should be well below 1s
        assert (beverage.last_modified - beverage.date_added).total_seconds() < 1

    def test_boolean_attributes(self):
        # Create without specifying a bool value
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            bottle_date="2013-06-24")

        # The for_trade attribute should be True by default
        assert beverage.for_trade is True
        assert beverage.to_dict()['for_trade'] is True

        # Set the bool
        beverage.for_trade = True
        assert beverage.for_trade is True
        assert beverage.to_dict()['for_trade'] is True

        # Flip the bool
        beverage.for_trade = False
        assert beverage.for_trade is False
        assert beverage.to_dict()['for_trade'] is False

        # Create w/bool = True
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            bottle_date="2013-06-24",
                            for_trade=True)

        assert beverage.for_trade is True
        assert beverage.to_dict()['for_trade'] is True

        # Create w/bool = False
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            bottle_date="2013-06-24",
                            for_trade=False)

        assert beverage.for_trade is False
        assert beverage.to_dict()['for_trade'] is False

    def test_attribute_changes(self):
        # Create with all available attributes
        beverage = Beverage(beverage_id="This Is My #2 BeverageId",
                            producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1,
                            last_modified=datetime.utcfromtimestamp(1586631578.640012))

        # Change some attributes and verify the changes stuck

    def test_model_creation(self):
        # Create with all available attributes using keyword args
        beverage = Beverage(beverage_id="This Is My #3 BeverageId",
                            producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home",
                            batch=1,
                            bottle_date="2013-06-24",
                            qty=14,
                            qty_cold=6,
                            style="Sour",
                            specific_style="Gose",
                            untappd="https://untappd.com/b/westbrook-brewing-co-gose/155824",
                            aging_potential=3,
                            trade_value=3,
                            for_trade=True,
                            note="My go-to when mowing the lawn.",
                            date_added="2020-04-10",
                            last_modified="2020-04-11")

        assert beverage.beverage_id == "This Is My #3 BeverageId"
        assert beverage.producer == "Westbrook"
        assert beverage.name == "Gose"
        assert beverage.year == 2013
        assert beverage.size == "12 oz"
        assert beverage.location == "Home"
        assert beverage.batch == 1
        assert beverage.bottle_date == "2013-06-24"
        assert beverage.qty == 14
        assert beverage.qty_cold == 6
        assert beverage.style == "Sour"
        assert beverage.specific_style == "Gose"
        assert beverage.untappd == "https://untappd.com/b/westbrook-brewing-co-gose/155824"
        assert beverage.aging_potential == 3
        assert beverage.trade_value == 3
        assert beverage.for_trade is True
        assert beverage.note == "My go-to when mowing the lawn."
        assert beverage.date_added == datetime.fromisoformat("2020-04-10")
        assert (beverage.last_modified - datetime.utcnow()).total_seconds() < 1

        # Same test, but created by parsing a dictionary
        beverage = Beverage(**default_beverage)

        assert beverage.beverage_id == "This Is My #4 BeverageId"
        assert beverage.producer == "Westbrook"
        assert beverage.name == "Gose"
        assert beverage.year == 2013
        assert beverage.size == "12 oz"
        assert beverage.location == "Home"
        assert beverage.batch == 1
        assert beverage.bottle_date == "2013-06-24"
        assert beverage.qty == 14
        assert beverage.qty_cold == 9
        assert beverage.style == "Sour"
        assert beverage.specific_style == "Gose"
        assert beverage.untappd == "https://untappd.com/b/westbrook-brewing-co-gose/155824"
        assert beverage.aging_potential == 3
        assert beverage.trade_value == 3
        assert beverage.for_trade is True
        assert beverage.note == "My go-to when mowing the lawn."
        assert beverage.date_added == datetime.fromisoformat("2020-04-10")
        assert (beverage.last_modified - datetime.utcnow()).total_seconds() < 1

    def test_to_dict(self):
        # Full default beverage converted to a dictionary
        beverage = Beverage(**default_beverage)
        beverage_dict = beverage.to_dict()

        assert isinstance(beverage_dict, dict)
        assert beverage_dict['beverage_id'] == "This Is My #4 BeverageId"
        assert beverage_dict['producer'] == "Westbrook"
        assert beverage_dict['name'] == "Gose"
        assert beverage_dict['year'] == 2013
        assert beverage_dict['size'] == "12 oz"
        assert beverage_dict['location'] == "Home"
        assert beverage_dict['batch'] == 1
        assert beverage_dict['bottle_date'] == "2013-06-24"
        assert beverage_dict['qty'] == 14
        assert beverage_dict['qty_cold'] == 9
        assert beverage_dict['style'] == "Sour"
        assert beverage_dict['specific_style'] == "Gose"
        assert beverage_dict['untappd'] == "https://untappd.com/b/westbrook-brewing-co-gose/155824"
        assert beverage_dict['aging_potential'] == 3
        assert beverage_dict['trade_value'] == 3
        assert beverage_dict['for_trade'] is True
        assert beverage_dict['note'] == "My go-to when mowing the lawn."

        # By default, the .to_dict() method returns the datetime fields as a `float` epoch
        assert beverage_dict['date_added'] == datetime.fromisoformat("2020-04-10").timestamp() * 1000
        assert isinstance(beverage_dict['last_modified'], float)

        # When providing the minimum required fields, the optional fields return as None
        beverage = Beverage(producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            location="Home")
        beverage_dict = beverage.to_dict()

        assert beverage_dict['beverage_id'] == "Westbrook_Gose_2013_12 oz_None"
        assert beverage_dict['producer'] == "Westbrook"
        assert beverage_dict['name'] == "Gose"
        assert beverage_dict['year'] == 2013
        assert beverage_dict['size'] == "12 oz"
        assert beverage_dict['location'] == "Home"
        assert beverage_dict['batch'] is None
        assert beverage_dict['bottle_date'] is None
        assert beverage_dict['qty'] == 0
        assert beverage_dict['qty_cold'] == 0
        assert beverage_dict['style'] is None
        assert beverage_dict['specific_style'] is None
        assert beverage_dict['untappd'] is None
        assert beverage_dict['aging_potential'] == 2  # Defaults to 2
        assert beverage_dict['trade_value'] is None
        assert beverage_dict['for_trade'] is True  # Defaults to True
        assert beverage_dict['note'] is None

        # The .to_dict() method returns the datetime fields as a `float` epoch
        now = datetime.timestamp(datetime.utcnow())
        assert abs(now - beverage_dict['date_added']) < 1
        assert abs(now - beverage_dict['last_modified']) < 1

    # def test_to_json(self):
    #     # Verify the output is json by calling json.loads() without raising an exception
    #     beverage_json = Beverage(**default_beverage).to_json()
    #     assert isinstance(json.loads(beverage_json), dict)

    def test_dunders(self):
        # Test the double-underscore methods
        beverage = Beverage(beverage_id="This Is My #4 BeverageId",
                            producer="Westbrook",
                            name="Gose",
                            year=2013,
                            size="12 oz",
                            batch=1,
                            location="Home")

        test_string = beverage.__repr__()
        assert isinstance(test_string, str)
        assert "This Is My #4 BeverageId" in test_string
        assert "Home" in test_string
