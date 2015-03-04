from pupa.scrape import Scraper, Person, Membership, Organization, Post
import subprocess

class UnitedStatesBillScraper(Scraper):

    def run_unitedstates_bill_scraper(self):
        """
        Runs the unitedstates scrapers using the virtualenv and data path set in UnitedStates.

        @return: void
        """
        from . import UnitedStates
        command = [UnitedStates.unitedstates_virtenv_bin_path, UnitedStates.unitedstates_congress_path + 'run', 'bills']
        process = subprocess.Popen(command, cwd=UnitedStates.unitedstates_data_path)
        process.wait()
        return

    def scrape_bills(self):
        """
        Does several things:

        1) Scrapes bill data from unitedstates project and saves the data to path specified in UnitedStates module
        2) Iterates over bill data and converts each one an OCD model.
        3) Yields the OCD-compliant bill model
        @return: yield
        """
        self.run_unitedstates_bill_scraper()
        """
        // TODO
        1) Iterate over file directory in UnitedStates.unitedstates_data_path
        2) Create Bill-compliant objects
        3) Yield them
        """


    def scrape(self):
        yield from self.scrape_bills()