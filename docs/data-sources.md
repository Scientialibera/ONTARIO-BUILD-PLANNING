# Public data sources

## Ontario Builds: key infrastructure projects

Official dataset:
https://data.ontario.ca/dataset/ontario-builds-key-infrastructure-projects

The dataset is updated quarterly and includes project name, category, supporting ministry, community, status, target completion, description, outcome, region, address, estimated publicly disclosed budget, funding-source indicators and coordinates when available.

The application uses English datastore resource ID `35dc5416-2b86-4a79-b3e6-acbfe004c81a`.

## City of Toronto Capital Projects Pipeline

Official dataset:
https://open.toronto.ca/dataset/capital-project-pipeline/

This is an advance notice dataset for capital projects expected to be competitively procured. The source explicitly warns that timing and details are preliminary and may change.

The backend resolves the current datastore resource dynamically through CKAN `package_show` rather than hard-coding the resource ID.

## City of Toronto Bids Solicitations

Official dataset:
https://open.toronto.ca/dataset/tobids-all-open-solicitations/

This dataset provides solicitation numbers, procurement type, issue dates, submission deadlines, category, description, division and buyer contact information. It is used to identify currently open records and compare them with the advance capital pipeline.

## Infrastructure Ontario context

Infrastructure Ontario publishes a project search and periodic market updates covering major projects in planning, procurement and construction. These sources are documented for analyst context but are not scraped by the first release.
