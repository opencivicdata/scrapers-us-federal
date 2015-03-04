from pupa.scrape import Jurisdiction, Organization

# config file, see example file for how to configure
from .config import Configuration

# scrapers
from .legislative import UnitedStatesLegislativeScraper
from .bill import UnitedStatesBillScraper

class UnitedStates(Jurisdiction, Configuration):
    classification = 'government'
    division_id = 'ocd-division/country:us'

    name = 'United States Federal Government'
    url = 'http://usa.gov/'

    parties = [
        {"name": "Republican",},
        {"name": "Democratic",},
        {"name": "Independent",},
    ]

    scrapers = {
        "congress": UnitedStatesLegislativeScraper,
        "bills": UnitedStatesBillScraper,
        # Executive Scraper here
    }

    def get_organizations(self):
        legislature = Organization("United States Congress",
                                   classification='legislature')
        yield legislature