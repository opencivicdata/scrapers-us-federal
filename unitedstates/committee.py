from pupa.scrape import Scraper, Organization
from urllib import request
import yaml

class UnitedStatesCommitteeScraper(Scraper):
    
    def fetch_yaml(self, source):
        committee_string = request.urlopen(source)
        return yaml.safe_load(committee_string)
    
    def scrape_committees(self, repos):
        for repo in repos:
            source = "https://raw.githubusercontent.com/unitedstates/congress-legislators/master/{0}".format(repo)
            committees = self.fetch_yaml(source)
            for committee in committees:
                org = Organization(committee['name'], 
                                   classification='committee')
                
                org.add_source(source)
                
                for key in committee.keys() &  {'url', 'rss_url'}:
                    org.add_link(committee[key])
                
                for key in committee.keys() & {'phone', 'address'}:
                    org.add_contact_detail(type='voice', value=committee[key]) if key == 'phone' else org.add_contact_detail(type=key, value=committee[key])

                for key in committee.keys() & {'senate_committee_id', 'house_committee_id', 'thomas_id'}:
                    org.add_identifier(committee[key], scheme=key)

                if 'subcommittees' in committee:
                    for subcommittee in committee['subcommittees']:
                        sub_org = Organization(subcommittee['name'], 
                                          classification="committee",
                                          parent_id = org._id)
                        
                        sub_org.add_identifier(subcommittee['thomas_id'], scheme="thomas")
                        sub_org.add_source(source)
                        
                        for key in subcommittee.keys() & {'phone', 'address'}:
                            sub_org.add_contact_detail(type='voice', value=committee[key]) if key == 'phone' else sub_org.add_contact_detail(type=key, value=committee[key])

                        yield sub_org

                yield org

    def scrape(self):
        yield from self.scrape_committees(['committees-historical.yaml', 'committees-current.yaml'])
