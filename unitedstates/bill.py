from pupa.scrape import Scraper, Person, Membership, Organization, Post, Bill
from pupa import settings

import subprocess
import os
import re
import json
import dateutil.parser

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            filename = os.path.join(root, basename)
            if re.match(pattern, filename):
                yield filename

class UnitedStatesBillScraper(Scraper):

    # https://github.com/unitedstates/congress/wiki/bills#basic-information
    TYPE_MAP = {
         # "H.R. 1234". It stands for House of Representatives, but it is the prefix used for bills introduced in the House.
        'hr': {'chamber':'lower', 'canonical': 'HR'},
         # "H.Res. 1234". It stands for House Simple Resolution.
        'hres': {'chamber':'lower', 'canonical': 'HRes'},
         # "H.Con.Res. 1234". It stands for House Concurrent Resolution.
        'hconres': {'chamber':'joint', 'canonical':'HConRes'},
         # "H.J.Res. 1234". It stands for House Joint Resolution.
        'hjres': {'chamber':'joint', 'canonical':'HJRes'},
         # "S. 1234". It stands for Senate and it is the prefix used for bills introduced in the Senate. Any abbreviation besides "S." is incorrect.
        's': {'chamber':'upper', 'canonical': 'S'},
         # "S.Res. 1234". It stands for Senate Simple Resolution.
        'sres': {'chamber':'upper', 'canonical': 'SRes'},
         # "S.Con.Res. 1234". It stands for Senate Concurrent Resolution.
        'sconres': {'chamber':'joint', 'canonical': 'SConRes'},
        # "S.J.Res. 1234". It stands for Senate Joint Resolution.
        'sjres': {'chamber':'joint', 'canonical': 'SJRes'}
    }

    TITLE_CHAMBER_MAP = {
        'Rep': 'lower',
        'Sen': 'upper'
    }

    # http://www.gpo.gov/help/index.html#about_congressional_bills.htm
    VERSION_MAP = {
        'eh': 'Engrossed in House',
        'rcs': 'Reference Change Senate',
        'iph': 'Indefinitely Postponed House',
        'cdh': 'Committee Discharged House',
        'ris': 'Referral Instructions Senate',
        'rah': 'Referred with Amendments House',
        'pwah': 'Ordered to be Printed with House Amendment',
        'ih': 'Introduced in House',
        'as': 'Amendment Ordered to be Printed Senate',
        'renr': 'Re-enrolled Bill',
        'ras': 'Referred with Amendments Senate',
        'rts': 'Referred to Committee Senate',
        'cds': 'Committee Discharged Senate',
        'sas': 'Additional Sponsors Senate',
        'lts': 'Laid on Table in Senate',
        'pap': 'Printed as Passed',
        'pp': 'Public Print',
        'rfh': 'Referred in House',
        'pav': 'Previous Action Vitiated',
        'ash': 'Additional Sponsors House',
        'pcs': 'Placed on Calendar Senate',
        'rs': 'Reported in Senate',
        'fph': 'Failed Passage House',
        'enr': 'Enrolled Bill',
        'rch': 'Reference Change House',
        'fps': 'Failed Passage Senate',
        'rh': 'Reported in House',
        'is': 'Introduced in Senate',
        'eah': 'Engrossed Amendment House',
        'reah': 'Re-engrossed Amendment House',
        'es': 'Engrossed in Senate',
        'ops': 'Ordered to be Printed Senate',
        'rth': 'Referred to Committee House',
        'fah': 'Failed Amendment House',
        'eas': 'Engrossed Amendment Senate',
        'oph': 'Ordered to be Printed House',
        'cph': 'Considered and Passed House',
        'lth': 'Laid on Table in House',
        'hds': 'Held at Desk Senate',
        'rds': 'Received in Senate',
        'ips': 'Indefinitely Postponed Senate',
        'rfs': 'Referred in Senate',
        'hdh': 'Held at Desk House',
        'ath': 'Agreed to House',
        'rih': 'Referral Instructions House',
        'pch': 'Placed on Calendar House',
        'ats': 'Agreed to Senate',
        'eph': 'Engrossed and Deemed Passed by House',
        'res': 'Re-engrossed Amendment Senate',
        'sc': 'Sponsor Change',
        'cps': 'Considered and Passed Senate',
        'rdh': 'Received in House'
    }

    def run_unitedstates_bill_scraper(self):
        """
        Runs the unitedstates scrapers using the virtualenv and data path set in UnitedStates.
        Must set environmental variables for the python virtualenv that you are using and the
        path for the unitedstates/congress project

        @return: void
        """
        try:
            us_congress_path = os.environ['US_CONGRESS_PATH']
            if not us_congress_path.endswith('/'): us_congress_path += '/'
            us_virtenv_python_bin_path = os.environ['US_VIRTENV_PYTHON_BIN_PATH']
            command = [us_virtenv_python_bin_path, us_congress_path + 'run', 'bills']
            process = subprocess.Popen(command, cwd=settings.SCRAPED_DATA_DIR)
            process.wait()
            command = [us_virtenv_python_bin_path, us_congress_path + 'run', 'bill_versions']
            process = subprocess.Popen(command, cwd=settings.SCRAPED_DATA_DIR)
            process.wait()
            return
        except KeyError:
            print('You must set environmental variables for the unitedstates/congress path (US_CONGRESS_PATH)'
                  'and the virtualenv python bin path (US_VIRTENV_PYTHON_BIN_PATH) for that project.')

    def scrape_bills(self):
        """
        Does the following

        1) Scrapes bill data from unitedstates project and saves the data to path specified in UnitedStates module
        2) Iterates over bill data and converts each one to an OCD-compliant bill model.
        3) Yields the OCD-compliant bill model instance
        @return: yield Bill instance
        """

        # run scraper first to pull in all the bill data
        self.run_unitedstates_bill_scraper()
        # iterate over all the files and build and yield Bill objects
        for filename in find_files(settings.SCRAPED_DATA_DIR, '.*[a-z]*\/[a-z]*[0-9]*\/data\.json'):
            try:
                with open(filename) as json_file:
                    json_data = json.load(json_file)
                    ## Initialize Object
                    bill = Bill(self.TYPE_MAP[json_data['bill_type']]['canonical'] + ' ' + json_data['number'],
                                json_data['congress'],
                                json_data['official_title'],
                                chamber=self.TYPE_MAP[json_data['bill_type']]['chamber']
                    )

                    ## Basics
                    bill.type = [json_data['bill_type']]
                    bill.subject = json_data['subjects']
                    bill.add_summary(json_data['summary']['as'], json_data['summary']['text'], json_data['summary']['date'])

                    ## Common Fields
                    bill.created_at = json_data['introduced_at']
                    bill.updated_at = dateutil.parser.parse(json_data['updated_at'])
                    # bill.sources = needs to get patched into unitedstates/congress

                    ## Other/Related Bills
                    bill.other_titles = [{'note':t['type'], 'title':t['title']} for t in json_data['titles']]
                    # change value of relationship_type to 'type' field from json_data when permitted by schema
                    bill.related_bills = [{'session': b['session'], 'name': b['name'], 'relationship_type':'companion'}
                                          for b in json_data['related_bills']]

                    ## Sponsors and Actions

                    # add primary sponsor
                    bill.add_sponsorship_by_identifier(json_data['sponsor']['name'],
                                                       'person',
                                                       'person',
                                                       True,
                                                       scheme='thomas_id',
                                                       identifier=json_data['sponsor']['thomas_id'],
                    )

                    # add cosponsors
                    for cs in json_data['cosponsors']:
                        bill.add_sponsorship_by_identifier(cs['name'],
                                                           'person',
                                                           'person',
                                                           False,
                                                           scheme='thomas_id',
                                                           identifier=cs['thomas_id']
                        )

                    # add actions
                    for action in json_data['actions']:
                        bill.actions.append({'date':action['acted_at'],
                                             'type':[action['type']],
                                             'description': action['text'],
                                             'actor': '???', # TODO
                                             'related_entities': []} # TODO
                        )

                    # add bill versions
                    for version_path in find_files(os.path.join(settings.SCRAPED_DATA_DIR,
                                                     'data',
                                                     bill.session,
                                                     'bills',
                                                     json_data['bill_type'],
                                                     json_data['bill_type'] + json_data['number'],
                                                     'text-versions'), '*\.json'):
                        try:
                            with open(version_path) as version_file:
                                version_json_data = json.load(version_file)
                                for k,v in version_json_data['urls'].iteritems():
                                    bill.add_version_link(version_json_data['version_code'],)

                                bill.versions = [{'date':version_json_data['issued_on'],
                                                  'type':version_json_data['version_code'],
                                                  'name':self.VERSION_MAP[version_json_data['version_code']],
                                                  'links': [{'mimetype':k, 'url':v}
                                                            for k,v in version_json_data['urls'].iteritems()]}]
                        except IOError:
                            print("Unable to open file with path " + version_path)

                    yield bill

            except IOError:
                print("Unable to open file with path " + filename)



    def scrape(self):
        yield from self.scrape_bills()