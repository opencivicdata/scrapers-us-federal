# Congress API Endpoints and How Their Data Will Be Modeled in OCD

This document records how we're translating data from the `@unitedstates` project to the OCD spec. For now, we'll have a section per Congress API endpoint.

## /committees

"A congressional committee is a legislative sub-organization in the United States Congress that handles a specific duty (rather than the general duties of Congress)." -- [Wikipedia](http://en.wikipedia.org/wiki/United_States_congressional_committee)

### OCD Object Mapping

`@unitedstates` Committees map to the Open Civic Data `Organization` object. Committee memberships are represented by `Membership` objects that connect to the `Posts` array on the `Organization` object.

*** At the federal level congress, house, and senate are all organizations.  House, Senate, and joint committees are all going
to have parent_ids linking to the congress organization. ***

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
parent_committee | parent_id


#### `Members` to `People` via `Posts` and `Memberships`

The `@unitedstates` project stores _current_ committee memberships in the `committee-membership-current.yml` file. We'll use this to build the OCD `Memberships` that connect `Organizations`' `Posts` to OCD `Person` objects.

### `Members`\' title to OCD `Post` Object.

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
bill_id 					  				| identifier
bill_type 									| classification
committees hash 						| * Not carried over *
introduced_at								| actions
congress 					  				| * application logic and/or extras *
enacted_as									| extras
number						  				| other_identifiers
official_title							| title
short_title									| * disregard *
popular_title								| * disregard *
titles 											| other_titles
status											| ? deduce from actions ?
status_at										| ? deduce from actions ?
subjects										| subject
subjects_top_term						| extras
sponsor											| sponsorship with 'sponsor' classificaiton
cosponsors									| sponships with 'cosponsor' classification
related_bills								| related_bills
summary		 									| abstracts
histories										| * disregard *
ammendments						| * waiting on OCD field *


## /votes

Recorded vote in the United States Congress, often called a roll-call vote.

The specific rules differs between the House and the Senate and both are afforded considerable freedom in establishing their own rules under Article One of the United States Constitution. -- See [Wikipedia](http://en.wikipedia.org/wiki/Roll_call) for more information.

### OCD Object Mapping

`@unitedstates` Votes map to the Open Civic Data `Vote` object. It's nearly a one-to-one attribute mapping. See `@unitedstates` votes data format [here](https://github.com/unitedstates/congress/wiki/votes) and OCD votes data format [here](http://docs.opencivicdata.org/en/latest/data/vote.html) for documentation of each.

### OCD Field Mapping

UnitedStates                | OCD Vote
--------------------------- | ---------------------------
vote_id 			| identifier
congress                     	| session
chamber                         | chamber (h -> lower, s -> upper, etc)
date                            | date
type                            | motion
category                        | type
result                          | passed
source_url                      | sources
bill                            | bill
? deduce from votes ?           | vote_counts
votes                           | roll_call

## /hearings

"Congressional hearings are the principal formal method by which committees collect and analyze information in the early stages of legislative policymaking" -- [Wikipedia](http://en.wikipedia.org/wiki/United_States_congressional_hearing)

### OCD Object Mapping

`@unitedstates` Committee Meetings map to the Open Civic Data `Event` object.

### OCD Field Mapping

UnitedStates                | OCD Event
--------------------------- | ---------------------------
guid/house_event_id/congress/house_meeting_type ???				| identifier
*generate*                     	| name
topic                           | description
occurs_at                       | when
				| end
ask paul                        | status
room		                | location (name)
committee			| participants (see mapping below)
witnesses                       | agenda (see mapping below)
bill_ids			| agenda (see mapping below)
meeting_documents		| media (see mapping below)
url				| links (see mapping below)

Should we derive the Person models from committee membership? Should the participating committee be only the subcommittee (if applicable) or both the subcommittee and the parent committee?

committe	  	  | OCD Event-participants
------------------------- | ---------------------------
chamber				| chamber
*derived*			| note
*default value*			| type = organization ?
committee 			| name
*derived*			| id

Should the organization (if applicable) only be associated with the person or both the person and the agenda?

witnesses		 | OCD Event-agenda
------------------------ | ---------------------------
documents			| media 
first_name, last_name, witness_type, position | related_entitites
organization			| related_entities 

Leave note field on the agenda empty?

bill_ids		 | OCD Event-agenda
------------------------ | ---------------------------
array entries are bill identifiers	| related_entities

This maps fairly nicely.

meeting_documents	 | OCD Event-media
------------------------ | ---------------------------
type				| type
name				| description
date				| published_on
urls				| links (mimetype = infer mimetype from url extension, url = url)
				| offset

What should the note be? The link in the US scrapers are to the committee repository whichh is basically an html representation of the hearing data.

url	 		 | OCD Event-links
------------------------ | ---------------------------
url			 | note = Calendar Event??? url=url

## /floor_updates

Recent real time, to-the-minute updates from the House and Senate floor. House floor updates are sourced from XML at the [House Clerk](http://clerk.house.gov/floorsummary/floor.aspx), and Senate updates from the [Senate Periodical Press Gallery](http://www.periodicalpress.senate.gov/).

### OCD Object Mapping

`House Clerk XML` and `Senate Periodic Press Gallery` map to the Open Civic Data `Event` object.

### OCD Field Mapping

#### House Clerk XML

The House releases XML for floor updates that we will ingest and translate directly.

XML                	    | OCD Event
--------------------------- | ---------------------------
*derived from chamber, action_time* 	| name
"floor_update"		    | classification
action_time[for-search]	    | start_time
?? eastern ??		    | timezone
action_description	            | description
capitol (get url/coords of chamber) 	| location
False				| all_day
				| end_time
confirmed			| status
Parse names?? ER?		| participants
a[rel='bill']			| agenda (type=bill)
a[rel='vote']			| agenda (type=vote)

#### Senate Periodic Press Gallery

The Senate does not release floor updates in a machine-readable format. We must parse the HTML. You can see a current [scraper](https://github.com/sunlightlabs/congress/blob/master/tasks/floor_senate/floor_senate.rb) on the Congress API. The mapping table below will translate from the Congress API fields as the scraper will be adapted for OCD.

Senate Periodic Press Gallery     | OCD Event
--------------------------------- | ---------------------------
*derived from chamber, action time*	| name
"floor_update"		    | classification
timestamp		    | start_time	
?? eastern ??		    | timezone
update  	            | description
capitol (get url/coords of chamber) 	| location
False				| all_day
				| end_time
confirmed			| status
bill_ids			| agenda (type=bill)
vote_ids			| agenda (type=vote)
Parse names?? ER?		| participants
