from pupa.scrape import Scraper, Person, Membership, Organization, Post
from pupa.utils import make_pseudo_id

from collections import defaultdict
import yaml


class UnitedStatesLegislativeScraper(Scraper):

    def yamlize(self, url):
        resp = self.urlopen(url)
        return yaml.safe_load(resp)

    def get_url(self, what):
        return ("https://raw.githubusercontent.com/"
              + "unitedstates/congress-legislators/master/"
              + what
              + ".yaml")

    def scrape_current_chambers(self):
        CURRENT_LEGISLATORS = self.get_url("legislators-current")

        house = Organization(
            name="United States House of Representatives",
            classification='legislature',
        )
        house.add_source(CURRENT_LEGISLATORS)
        self.house = house
        yield house

        senate = Organization(
            name="United States Senate",
            classification='legislature',
        )
        senate.add_source(CURRENT_LEGISLATORS)
        self.senate = senate
        yield senate

    def scrape_current_legislators(self):
        CURRENT_LEGISLATORS = self.get_url("legislators-current")

        people = self.yamlize(CURRENT_LEGISLATORS)
        parties = set()
        person_cache = defaultdict(lambda: defaultdict(lambda: None))

        for person in people:
            name = person['name'].get('official_full')
            if name is None:
                name = "{name[first]} {name[last]}".format(**person)

            birth_date = person['bio']['birthday']

            who = person_cache[name][birth_date]
            has_term = False

            if who is None:
                who = Person(name=name, birth_date=birth_date)
                who.add_source(url=CURRENT_LEGISLATORS,
                               note="unitedstates project on GitHub")

            for term in person.get('terms', []):
                has_term = True
                start_date = term['start']
                end_date = term['end']
                state = term['state']
                type_ = term['type']
                district = term.get('district', None)
                party = term.get('party', None)

                chamber = {'rep': 'lower',
                           'sen': 'upper',}[type_]

                role = {'rep': 'Representative',
                        'sen': 'Senator',}[type_]

                if type_ == "rep" and district is not None:
                    label = "%s for District %s" % (role, district)

                    division_id = ("ocd-division/country:us/"
                                   "state:{state}/cd:{district}".format(
                                       state=state.lower(), district=district))

                    post = Post(organization_id={
                            "rep": self.house,
                            "sen": self.senate
                        }[type_]._id,
                        division_id=division_id,
                        label=label, role=role)
                    yield post

                    membership = Membership(
                        post_id=post._id,
                        role=role,
                        label=label,
                        start_date=start_date,
                        end_date=end_date,
                        person_id=who._id,
                        organization_id={
                            "rep": self.house,
                            "sen": self.senate,
                        }[type_]._id)
                    yield membership

                if type_ == "sen":

                    division_id = ("ocd-division/country:us/state:{state}".format(
                        state=state.lower()))

                    label = "Senitor for %s" % (state)
                    post = Post(organization_id={
                            "rep": self.house,
                            "sen": self.senate
                        }[type_]._id,
                        division_id=division_id,
                        label=label, role=role)
                    yield post

                    membership = Membership(
                        post_id=post._id,
                        role=role,
                        label=label,
                        start_date=start_date,
                        end_date=end_date,
                        person_id=who._id,
                        organization_id={
                            "rep": self.house,
                            "sen": self.senate,
                        }[type_]._id)
                    yield membership

                if party == "Democrat":
                    party = "Democratic"

                if party:
                    membership = Membership(
                        role='member',
                        start_date=start_date,
                        end_date=end_date,
                        person_id=who._id,
                        organization_id=make_pseudo_id(
                            classification="party",
                            name=party))
                    yield membership

            for key, value in person.get('id', {}).items():
                if isinstance(value, list):
                    for v in value:
                        who.add_identifier(str(v), scheme=key)
                else:
                    who.add_identifier(str(value), scheme=key)

            if has_term:
                yield who

    def scrape(self):
        yield from self.scrape_current_chambers()
        yield from self.scrape_current_legislators()
