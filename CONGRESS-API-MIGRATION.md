# Congress API Endpoints and How Their Data Will Be Modeled in OCD

This document records how we're translating data from the `@unitedstates` project to the OCD spec. For now, we'll have a section per Congress API endpoint.

## /committees

"A congressional committee is a legislative sub-organization in the United States Congress that handles a specific duty (rather than the general duties of Congress)." -- [Wikipedia](http://en.wikipedia.org/wiki/United_States_congressional_committee)

### OCD Object Mapping

`@unitedstates` Committees map to the Open Civic Data `Organization` object. Committee memberships are represented by `Membership` objects that connect to the `Posts` array on the `Organization` object.

### OCD Field Mapping 

#### `Committees` to `Organizations`

UnitedStates  | OCD Organization
------------- | -------------
type		  | handled by parent_id and application logic
name 		  | name
url			  | .links
thomas_id	  | .identifiers (scheme: THOMAS)
phone		  | .contact_details
address       | .contact_details
rss_url:	  | .links
jurisdiction  | .extras   

#### `Members` to `People` via `Posts` and `Memberships`

The `@unitedstates` project stores _current_ committee memberships in the `committee-membership-current.yml` file. We'll use this to build the OCD `Memberships` that connect `Organizations`' `Posts` to OCD `Person` objects.

UnitedStates                | OCD Post
--------------------------- | ---------------------------
party (majority or minority)| handled by application logic
title 						| label
							| role
							| organization_id
							| division_id
							| start_date
							| end_date
							| contact_details
							| links
							| extras


UnitedStates                | OCD Membership
--------------------------- | ---------------------------
rank						| .extras
							| label
							| role
							| person_id
							| organization_id
							| post_id
							| on_behalf_of_id
							| start_date
							| end_date
							| contact_details
							| links
							| extras
							| jurisdiction_id
							| division_id

### Notes

There is no good idea of _time_ in our current store of committees and committee membership, partially because there is not great historical committee data. More details on this issue: https://github.com/unitedstates/congress-legislators/issues/46.

## /bills

UnitedStates                | OCD Bill
--------------------------- | ---------------------------
bill_id 					| identifier
bill_type 					| ? classification
committees hash 			| actions (related_entities field)
introduced_at				| actions
congress 					| application logic and/or extras
enacted_as					| extras
number						| ? necessary
official_title				| title
short_title					| other_titles
popular_title				| other_titles
titles 						| other_titles
status						| ? deduce from actions ?
status_at					| ? deduce from actions ?
subjects					| subject
subjects_top_term			| extras



