from pupa.scrape import Jurisdiction

from .legislative import UnitedStatesLegislativeScraper


class UnitedStates(Jurisdiction):
    jurisdiction_id = 'ocd-jurisdiction/country:us/government'
    division_id = 'ocd-division/country:us'

    name = 'United States Federal Government'
    url = 'http://usa.gov/'

    scrapers = {
        "congress": UnitedStatesLegislativeScraper,
    }
