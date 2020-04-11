from backend.models import Beer
from datetime import datetime
import pytest


class TestBeerModel:

    def test_required_attributes(self):
        # Must provide values for brewery, beer name, year, and size
        with pytest.raises(KeyError):
            beer = Beer()

        # Missing brewery
        with pytest.raises(KeyError):
            beer = Beer(name="Duff Lite",
                        year=1997,
                        size="12 oz",
                        bottle_date="1997-08-19",
                        batch=3)

        # Missing name
        with pytest.raises(KeyError):
            beer = Beer(brewery="Duff",
                        year=1997,
                        size="12 oz",
                        bottle_date="1997-08-19",
                        batch=3)

        # Missing year
        with pytest.raises(KeyError):
            beer = Beer(brewery="Duff",
                        name="Duff Lite",
                        size="12 oz",
                        bottle_date="1997-08-19",
                        batch=3)

        # Missing size
        with pytest.raises(KeyError):
            beer = Beer(brewery="Duff",
                        name="Duff Lite",
                        year=1997,
                        bottle_date="1997-08-19",
                        batch=3)

        # Year must be int (or convert to int)
        with pytest.raises(ValueError):
            beer = Beer(brewery="Duff",
                        name="Duff Lite",
                        year="Nineteen Ninety-Seven",
                        size="12 oz",
                        batch=5)

        # Batch must be int (or convert to int)
        with pytest.raises(ValueError):
            beer = Beer(brewery="Duff",
                        name="Duff Lite",
                        year=1997,
                        size="12 oz",
                        batch="Eskimo")

    def test_beer_id_creation(self):
        # Generates beer_id when not provided
        #  Ex: brewery_BeerName_year_size_{BottleDate or batch}
        # Should produce a fully-formed concatenated beer_id w/bottle_date
        beer = Beer(brewery="Duff",
                    name="Duff Lite",
                    year=1997,
                    size="12 oz",
                    bottle_date="1997-08-19")
        assert beer.beer_id == "Duff_Duff Lite_1997_12 oz_1997-08-19"

        # Should produce a fully-formed concatenated beer_id w/batch
        beer = Beer(brewery="Duff",
                    name="Duff Lite",
                    year=1997,
                    size="12 oz",
                    batch=3)
        assert beer.beer_id == "Duff_Duff Lite_1997_12 oz_3"

        #  When both bottle_date & batch are provided, bottle_date is used
        beer = Beer(brewery="Duff",
                    name="Duff Lite",
                    year=1997,
                    size="12 oz",
                    bottle_date="1997-08-19",
                    batch=3)
        assert beer.beer_id == "Duff_Duff Lite_1997_12 oz_1997-08-19"

        # With batch & bottle date both omitted, the beer_id generated should end with "_None"
        beer = Beer(brewery="Duff",
                    name="Duff Lite",
                    year=1997,
                    size="12 oz")
        assert beer.beer_id == "Duff_Duff Lite_1997_12 oz_None"

    def test_beer_id(self):
        # When provided with a beer_id, a new one shouldn't be generated
        beer = Beer(beer_id="This Is My #1 BeerId",
                    brewery="Duff",
                    name="Duff Lite",
                    year=1997,
                    size="12 oz")
        assert beer.beer_id == "This Is My #1 BeerId"

    def test_datetime_attributes(self):
        # When date_added and/or last_modified aren't specified, they should be created
        beer = Beer(beer_id="This Is My #2 BeerId",
                    brewery="Duff",
                    name="Duff Lite",
                    year=1997,
                    size="12 oz",
                    batch=6)

        assert isinstance(beer.date_added, datetime)
        assert isinstance(beer.last_modified, datetime)
